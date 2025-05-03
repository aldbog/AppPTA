
from flask import Blueprint, render_template
from PaginaTA.db import get_db_connection

cercetare_bp = Blueprint('cercetare', __name__, template_folder="../templates")

@cercetare_bp.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cercetare LIMIT 5;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("cercetare.html", rows=rows)
