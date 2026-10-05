import hmac
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)


@app.get("/")
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