from flask import Flask, jsonify, request, render_template, redirect, url_for
import uuid

app = Flask(__name__)

# Banco de dados simples em memória
estoque = [
    {"id": 1, "nome_peca": "Pneu Traseiro 90/90-18", "quantidade": 5, "preco": 180.0},
    {"id": 2, "nome_peca": "Óleo de Motor 1L", "quantidade": 12, "preco": 35.0},
    {"id": 3, "nome_peca": "Kit Relação", "quantidade": 3, "preco": 120.0}
]

ordens = []

# ------------------- TELA -------------------

@app.route('/')
def pagina():
    return render_template('index.html', estoque=estoque)


# ------------------- ESTOQUE -------------------

@app.route('/estoque', methods=['GET'])
def ver_estoque():
    return jsonify(estoque)


@app.route('/estoque', methods=['POST'])
def cadastrar_peca():

    if request.is_json:
        dados = request.json
        nome = dados.get("nome_peca")
        quantidade = dados.get("quantidade", 0)
        preco = dados.get("preco", 0.0)
    else:
        nome = request.form.get("nome_peca")
        quantidade = int(request.form.get("quantidade", 0))
        preco = float(request.form.get("preco", 0.0))

    nova_peca = {
        "id": len(estoque) + 1,
        "nome_peca": nome,
        "quantidade": quantidade,
        "preco": preco
    }

    estoque.append(nova_peca)

    # REDIRECT CORRIGIDO (evita erro do navegador)
    return redirect(url_for('pagina'))


@app.route('/estoque/<int:id>', methods=['DELETE'])
def deletar_peca(id):
    for item in estoque:
        if item["id"] == id:
            estoque.remove(item)
            return jsonify({"msg": "removido"})

    return jsonify({"erro": "não encontrado"}), 404


# ------------------- ORDENS -------------------

@app.route('/os', methods=['POST'])
def criar_ordem():
    dados = request.json

    ordem = {
        "id": str(uuid.uuid4())[:8],
        "cliente": dados.get("cliente"),
        "moto": dados.get("moto"),
        "problema": dados.get("descricao"),
        "fotos": [],
        "status": "em andamento"
    }

    ordens.append(ordem)
    return jsonify(ordem), 201


@app.route('/os/<id>/foto', methods=['PATCH'])
def add_foto(id):
    for ordem in ordens:
        if ordem["id"] == id:
            ordem["fotos"].append("foto.jpg")
            return jsonify({"msg": "foto adicionada", "ordem": ordem})

    return jsonify({"erro": "ordem não encontrada"}), 404


# ------------------- RODAR -------------------

if __name__ == '__main__':
    app.run()
