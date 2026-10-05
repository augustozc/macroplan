
import hmac
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)


@app.get("/")
def index():
    return render_template_string("""
    <!doctype html>
    <html lang="pt-BR">
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Agente Macro</title>
      <h1>Agente Macro</h1>
      <label>APP_TOKEN:
        <input id="token" type="password" autocomplete="off">
      </label>
      <button id="run">Gerar relatório</button>
      <pre id="result"></pre>
      <script>
        document.getElementById("run").onclick = async () => {
          const result = document.getElementById("result");
          result.textContent = "Executando...";
          try {
            const response = await fetch("/generate", {
              method: "POST",
              headers: {
                "Authorization": "Bearer " + document.getElementById("token").value
              }
            });
            const data = await response.json();
            result.textContent = JSON.stringify(data, null, 2);
          } catch (error) {
            result.textContent = "Erro: " + error;
          }
        };
      </script>
    </html>
    """)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/generate")
def generate():
    token = os.getenv("APP_TOKEN")
    supplied = request.headers.get("Authorization", "").removeprefix("Bearer ")

    if not token:
        return jsonify(error="APP_TOKEN não configurado"), 503
    if not hmac.compare_digest(supplied, token):
        return jsonify(error="Não autorizado"), 401

    try:
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "agente.py")],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return jsonify(error="Tempo limite ao executar o agente"), 504

    if result.returncode != 0:
        app.logger.error("Falha no agente: %s", result.stderr)
        return jsonify(error="Falha ao executar o agente"), 502

    return jsonify(status="concluído", output=result.stdout)