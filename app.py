from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "abc-cacambas-secret-2026")

DATA_DIR = os.environ.get("DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)
PEDIDOS_FILE = os.path.join(DATA_DIR, "pedidos.json")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "abc2026")

def load_pedidos():
    if not os.path.exists(PEDIDOS_FILE):
        return []
    try:
        with open(PEDIDOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_pedidos(pedidos):
    with open(PEDIDOS_FILE, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/pedido", methods=["POST"])
def api_pedido():
    data = request.json or request.form
    pedido = {
        "id": len(load_pedidos()) + 1,
        "nome": data.get("nome", ""),
        "cep": data.get("cep", ""),
        "tamanho": data.get("tamanho", ""),
        "detalhes": data.get("detalhes", ""),
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "ip": request.remote_addr
    }
    pedidos = load_pedidos()
    pedidos.append(pedido)
    save_pedidos(pedidos)
    return jsonify({"ok": True, "id": pedido["id"]})

@app.route("/admin")
@login_required
def admin():
    pedidos = load_pedidos()
    return render_template("admin.html", pedidos=pedidos, total=len(pedidos))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("user") == ADMIN_USER and request.form.get("pass") == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("login.html", erro="Usuário ou senha incorretos")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
