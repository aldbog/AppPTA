
from flask import Flask, render_template
from PaginaTA.Pontaj.routes import pontaj_bp
from PaginaTA.Cercetare.routes import cercetare_bp

app = Flask(__name__, template_folder="PaginaTA/templates")

app.register_blueprint(pontaj_bp, url_prefix="/pontaj")
app.register_blueprint(cercetare_bp, url_prefix="/cercetare")

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
