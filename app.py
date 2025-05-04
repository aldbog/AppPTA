import os
from flask import Flask, request, jsonify, render_template
import psycopg2

from PaginaTA.Pontaj.routes import pontaj_bp
from PaginaTA.Cercetare.routes import cercetare_bp

app = Flask(__name__, template_folder="PaginaTA/templates")

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
def verifica_email():
    email = request.args.get("email", "").strip().lower()

    # Verificare domeniu UVT
    if not email or not email.endswith("@e-uvt.ro"):
        return jsonify({
            "uvt": 0,
            "paginata_dru": 0,
            "ang_proiecte": 0,
            "ang_ai": 0,
            "dep_ang_proiecte": "-"
        })

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT paginata_dru, ang_proiecte, ang_ai, dep_ang_proiecte
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
            "dep_ang_proiecte": row[3] if row[3] else "-"
        })
    else:
        return jsonify({
            "uvt": 1,
            "paginata_dru": 0,
            "ang_proiecte": 0,
            "ang_ai": 0,
            "dep_ang_proiecte": "-"
        })

if __name__ == "__main__":
    app.run(host="0.
