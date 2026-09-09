"""
app.py
-------
Backend Flask do Assistente Cardiológico Inteligente (CardioIA - Fase 5).

Expõe uma API simples que a interface HTML consome:
  POST /mensagem  { "session_id": "...", "mensagem": "..." }  -> { "resposta": "..." }

Esta camada é só "porta de entrada" HTTP - toda a inteligência
(intents, entidades, diálogo) mora em nlu_engine.py, entities.py e
dialog_manager.py, mantendo o código organizado e fácil de explicar
no relatório.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dialog_manager import GerenciadorDialogo

app = Flask(__name__)
CORS(app)  # permite que o frontend (GitHub Pages) chame esta API de outro domínio

gerenciador = GerenciadorDialogo()


@app.route("/", methods=["GET"])
def raiz():
    return jsonify({
        "status": "online",
        "servico": "CardioIA - Assistente Cardiológico Inteligente (Fase 5)"
    })


@app.route("/mensagem", methods=["POST"])
def mensagem():
    dados = request.get_json(silent=True) or {}
    session_id = dados.get("session_id", "sessao_padrao")
    texto = dados.get("mensagem", "").strip()

    if not texto:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

    resposta = gerenciador.processar(session_id, texto)
    return jsonify({"resposta": resposta})


if __name__ == "__main__":
    # Uso local/Colab. Em produção (Render), o gunicorn chama "app:app" direto.
    app.run(host="0.0.0.0", port=5000, debug=True)
