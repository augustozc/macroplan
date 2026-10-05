# Agente Macro — POC

Protótipo de consulta de indicadores econômicos do SGS/Banco Central e apoio à análise de estresse patrimonial com Groq.

## Requisitos

- Python 3.10 ou superior
- Uma chave de API Groq configurada localmente no arquivo `.env`

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure no `.env` as variáveis exigidas pelo código. **Não publique esse arquivo nem compartilhe suas chaves.**

## Execução

```bash
python app.py
```

## Arquivos

- `app.py` — aplicação
- `agente.py` — lógica do agente e consulta ao SGS/Bacen
- `Relatorio_Estresse_Patrimonial.md` — relatório de estresse patrimonial
