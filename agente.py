import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("GROQ_API_KEY não está configurada.")

client = Groq(api_key=API_KEY)
MODELO = "openai/gpt-oss-20b"


def consultar_sgs_bacen(codigo_serie: int, data_inicio: str = "01/01/2026") -> str:
    """Consulta os dados mais recentes de uma série do SGS/Banco Central."""
    url = (
        "https://api.bcb.gov.br/dados/serie/"
        f"bcdata.sgs.{codigo_serie}/dados"
    )
    parametros = {
        "formato": "json",
        "dataInicial": data_inicio,
        "dataFinal": datetime.now().strftime("%d/%m/%Y"),
    }

    response = requests.get(url, params=parametros, timeout=20)
    response.raise_for_status()

    dados = response.json()
    if not isinstance(dados, list) or not dados:
        raise RuntimeError(f"O SGS não retornou dados para a série {codigo_serie}.")

    recentes = dados[-5:]
    return "; ".join(
        f"{item.get('data')}: {item.get('valor')}" for item in recentes
    )


def gerar_relatorio() -> Path:
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY não está configurada.")

    hoje = datetime.now()
    dados_selic = consultar_sgs_bacen(1)
    dados_ipca = consultar_sgs_bacen(433)

    prompt = f"""
Data da análise: {hoje.strftime("%d/%m/%Y")}.

Dados recentes consultados no SGS do Banco Central:
- Série 1 (Selic): {dados_selic}
- Série 433 (IPCA): {dados_ipca}

Analise, como exercício hipotético e não como recomendação financeira, uma
carteira de R$ 860.000,00 aplicada em Tesouro Selic, com retiradas mensais
de R$ 11.000,00, durante 36 meses.

Escreva em português e em Markdown. Inclua:
1. Diagnóstico e limitações dos dados disponíveis.
2. Projeção ilustrativa do fluxo de caixa e do consumo de capital em 36 meses.
3. Explicação das premissas usadas para juros, inflação, impostos e retiradas.
4. Análise do poder de compra, distinguindo valores nominais e reais.
5. Conclusão e nota de confiabilidade.

Não invente taxas futuras nem apresente projeções como garantidas. Se os dados
fornecidos não forem suficientes para um cálculo exato, declare as premissas
necessárias e deixe isso claro. Não afirme conhecer eventos futuros.
""".strip()

    print("[Executando] Enviando solicitação para a Groq...", flush=True)

    resposta = client.chat.completions.create(
        model=MODELO,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um analista financeiro cuidadoso. Diferencie fatos, "
                    "premissas e projeções; não invente dados nem prometa resultados."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    conteudo = resposta.choices[0].message.content
    if not conteudo or not conteudo.strip():
        raise RuntimeError("A Groq retornou conteúdo vazio para o relatório.")

    # O web.py executa o agente com uma pasta temporária como diretório atual.
    caminho_relatorio = (
        Path.cwd() / "Relatorio_Estresse_Patrimonial.md"
    ).resolve()
    caminho_relatorio.parent.mkdir(parents=True, exist_ok=True)
    caminho_relatorio.write_text(conteudo.strip() + "\n", encoding="utf-8")

    return caminho_relatorio


if __name__ == "__main__":
    print("--- Iniciando geração do relatório macroeconômico ---", flush=True)
    print(f"Data: {datetime.now():%Y-%m-%d %H:%M:%S}", flush=True)

    try:
        arquivo = gerar_relatorio()
        print(f"Relatório gerado: {arquivo}", flush=True)
    except Exception as erro:
        print(f"Erro ao gerar relatório: {erro}", file=sys.stderr, flush=True)
        sys.exit(1)