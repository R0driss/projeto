from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import uuid
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "segredo123"

ARQUIVO = "estoque.json"

# ========================
# USUÁRIOS (SIMPLES)
# ========================
usuarios = [
    {"username": "admin", "senha": generate_password_hash("123"), "tipo": "admin"},
    {"username": "cliente", "senha": generate_password_hash("123"), "tipo": "cliente"}
]

# ========================
# LOGIN
# ========================
@app.route('/login', methods=['POST'])
def login():
    dados = request.form

    for u in usuarios:
        if u["username"] == dados.get("username") and check_password_hash(u["senha"], dados.get("senha")):
            session["usuario"] = {
                "username": u["username"],
                "tipo": u["tipo"]
            }
            return redirect(url_for('pagina'))

    return "Login inválido", 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pagina'))

# ========================
# FUNÇÕES JSON
# ========================
def carregar_estoque():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r") as f:
        return json.load(f)


def salvar_estoque(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

# ========================
# TELA
# ========================
@app.route('/')
def pagina():
    estoque = carregar_estoque()
    usuario = session.get("usuario")
    return render_template('index.html', estoque=estoque, usuario=usuario)

# ========================
# ESTOQUE
# ========================
@app.route('/estoque', methods=['GET'])
def ver_estoque():
    estoque = carregar_estoque()
    return jsonify(estoque)


@app.route('/estoque', methods=['POST'])
def cadastrar_peca():

    usuario = session.get("usuario")
    if not usuario or usuario["tipo"] != "admin":
        return "Acesso negado", 403

    estoque = carregar_estoque()
    dados = request.form

    nova_peca = {
        "id": len(estoque) + 1,
        "nome_peca": dados.get("nome_peca"),
        "quantidade": int(dados.get("quantidade", 0)),
        "preco": float(dados.get("preco", 0.0))
    }

    estoque.append(nova_peca)
    salvar_estoque(estoque)

    return redirect(url_for('pagina'))


@app.route('/estoque/<int:id>', methods=['POST'])
def deletar_peca(id):

    usuario = session.get("usuario")
    if not usuario or usuario["tipo"] != "admin":
        return "Acesso negado", 403

    estoque = carregar_estoque()
    estoque = [item for item in estoque if item["id"] != id]

    salvar_estoque(estoque)

    return redirect(url_for('pagina'))

# ========================
# ORDENS
# ========================
@app.route('/os', methods=['POST'])
def criar_ordem():

    usuario = session.get("usuario")
    if not usuario:
        return "Precisa estar logado", 401

    dados = request.json

    ordem = {
        "id": str(uuid.uuid4())[:8],
        "cliente": usuario["username"],
        "moto": dados.get("moto"),
        "problema": dados.get("descricao"),
        "fotos": [],
        "status": "em andamento"
    }

    return jsonify(ordem), 201

# ========================
# RODAR
# ========================
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000)