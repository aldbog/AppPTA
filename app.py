
from flask import Flask, render_template
from PaginaTA.Pontaj.routes import pontaj_bp
from PaginaTA.Cercetare.routes import cercetare_bp

app = Flask(__name__, template_folder="PaginaTA/templates")

app.register_blueprint(pontaj_bp, url_prefix="/pontaj")
app.register_blueprint(cercetare_bp, url_prefix="/cercetare")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verificaemail")
def verifica_email():
    email = request.args.get("email")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT paginataintare, cercetareintrare
        FROM useriapp
        WHERE email = %s
    """, (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return jsonify({
            "found": True,
            "paginataintare": row[0],
            "cercetareintrare": row[1]
        })
    else:
        return jsonify({"found": False})

if __name__ == "__main__":
    app.run(debug=True)
