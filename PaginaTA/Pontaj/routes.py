
from flask import Blueprint, render_template
from PaginaTA.db import get_db_connection

pontaj_bp = Blueprint('pontaj', __name__, template_folder="../templates")

@pontaj_bp.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pontaj LIMIT 5;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("pontaj.html", rows=rows)
