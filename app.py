import os
from flask import Flask, request, jsonify, render_template
import psycopg2
from flask_cors import CORS

from PaginaTA.Pontaj.routes import pontaj_bp
from PaginaTA.Cercetare.routes import cercetare_bp

app = Flask(__name__, template_folder="PaginaTA/templates")
CORS(app)  # ✅ Apel după inițializarea lui `app`

API_KEY = "uvt2014"  # 🔐 setează un token secret aici
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = (
            request.headers.get("Authorization") or
            request.args.get("api_key") or
            request.cookies.get("api_key")
        )

        # Normalizează formatul (ex: "Bearer secrettoken123")
        if token and token.startswith("Bearer "):
            token = token[7:]

        if token != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated_function


app.register_blueprint(pontaj_bp, url_prefix="/pontaj")
app.register_blueprint(cercetare_bp, url_prefix="/cercetare")

# Funcția de conectare la Railway
def get_db_connection():
    return psycopg2.connect(
        host="nozomi.proxy.rlwy.net",
        database="railway",
        user="postgres",
        password="EeXrqIxEarrSNiJRwyrfgNwONgKqHMWx",
        port=53046
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verificaemail")
@require_api_key
def verifica_email():

    email = request.args.get("email", "").strip().lower()

    # Verificare domeniu UVT
    if not email or not email.endswith("@e-uvt.ro"):
        return jsonify({
            "uvt": 0,
            "paginata_dru": 0,
            "ang_proiecte": 0,
            "ang_ai": 0,
	    "admin": 0,
            "dep_ang_proiecte": "-"
        })

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT paginata_dru, ang_proiecte, ang_ai, dep_ang_proiecte, admin

        FROM useriapp
        WHERE email = %s
    """, (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return jsonify({
            "uvt": 1,
            "paginata_dru": row[0],
            "ang_proiecte": row[1],
            "ang_ai": row[2],
	    "admin": row[4],
            "dep_ang_proiecte": row[3] if row[3] else "-"
        })
    else:
        return jsonify({
            "uvt": 1,
            "paginata_dru": 0,
            "ang_proiecte": 0,
            "ang_ai": 0,
	    "admin": 0,
            "dep_ang_proiecte": "-"
        })



@app.route("/api/get")
@require_api_key
def get_record():
    table = request.args.get("table")
    key = request.args.get("key")
    value = request.args.get("value")

    if not table or not key or not value:
        return jsonify({"success": False, "error": "Parametri lipsă"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # ⚠️ Validare minimă a numelui tabelului și câmpului (evită SQL injection)
        if not table.isidentifier() or not key.isidentifier():
            return jsonify({"success": False, "error": "Parametri invalizi"}), 400

        query = f"SELECT * FROM {table} WHERE {key} = %s"
        cur.execute(query, (value,))
        row = cur.fetchone()

        if row is None:
            return jsonify({})

        # Extragem numele coloanelor
        columns = [desc[0] for desc in cur.description]
        result = dict(zip(columns, row))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()



@app.route("/api/update", methods=["POST"])
@require_api_key
def api_update():
    data = request.get_json()
    table = data.get("table")
    key = data.get("key")
    value = data.get("value")
    updates = data.get("data")  # Dicționar doar cu coloanele pe care le vrei modificate

    if not all([table, key, value, updates]):
        return jsonify({"error": "Parametri lipsă"}), 400

    # Validări de siguranță
    if not table.isidentifier() or not key.isidentifier():
        return jsonify({"error": "Parametri invalizi"}), 400

    # Construiește SET col1 = %s, col2 = %s ...
    set_clause = ", ".join([f"{col} = %s" for col in updates.keys()])
    values = list(updates.values()) + [value]  # valori + valoarea cheii la final

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"UPDATE {table} SET {set_clause} WHERE {key} = %s", values)
        conn.commit()
        return jsonify({"status": "updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()



# POST: Insert în tabelă
@app.route("/api/insert", methods=["POST"])
@require_api_key
def api_insert():
    data = request.get_json()
    table = data.get("table")
    fields = data.get("data")
    if not all([table, fields]):
        return jsonify({"error": "Parametri lipsă"}), 400

    keys = fields.keys()
    placeholders = ", ".join(["%s"] * len(keys))
    columns = ", ".join(keys)
    values = list(fields.values())

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "inserted"})



# POST: Ștergere după cheia primară
@app.route("/api/delete", methods=["POST"])
@require_api_key
def api_delete():
    data = request.get_json()
    table = data.get("table")
    key = data.get("key")
    value = data.get("value")
    if not all([table, key, value]):
        return jsonify({"error": "Parametri lipsă"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {key} = %s", (value,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/api/all")
@require_api_key
def api_get_all():
    table = request.args.get("table")

    if not table or not table.isidentifier():
        return jsonify({"success": False, "error": "Nume tabel invalid"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
