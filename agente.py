import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
# IMPORTAÇÃO SOBERANA: Usando o cliente nativo da própria Groq
from groq import Groq

# 1. CONFIGURAÇÃO DE AMBIENTE E CLIENTE OFICIAL
load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("ERRO CRÍTICO: GROQ_API_KEY não encontrada no arquivo .env")

# Instanciação nativa sem necessidade de alterar base_url manualmente
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Usando o modelo estável padrão da nuvem Groq
MODELO = "openai/gpt-oss-20b"


# 2. RESOLUÇÃO DE INTEGRAÇÃO - CONSUMO DA API DO BANCO CENTRAL DO BRASIL (SGS)
def consultar_sgs_bacen(codigo_serie: int, data_inicio: str = "01/01/2026") -> str:
    url = (
        f"https://api.bcb.gov.br/dados/serie/"
        f"bcdata.sgs.{codigo_serie}/dados"
        f"?formato=json&dataInicial={data_inicio}"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados)
            ultimos_dados = df.tail(5).to_dict(orient="records")
            return f"Dados Recentes da Série {codigo_serie}: {str(ultimos_dados)}"
        else:
            return f"Erro HTTP {response.status_code} na API do BACEN."
    except Exception as e:
        return f"Falha de comunicação na causa raiz: {str(e)}"


# 3. PIPELINE DE EXECUÇÃO
if __name__ == "__main__":
    print(f"--- Iniciando Processamento Macroeconômico Nativo via Groq SDK ---")
    print(f"Data Base: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Bloco 1: Coleta de Dados via API do Governo brasileiro
    print("[Executando] Agente Analista extraindo dados do BACEN...")
    dados_selic = consultar_sgs_bacen(1)   # Código 1 = Selic mensal
    dados_ipca = consultar_sgs_bacen(433)  # Código 433 = IPCA mensal
    
    contexto_dados = (
        f"Métricas extraídas em {datetime.now().strftime('%d/%m/%Y')}:\n"
        f"- Selic Recente: {dados_selic}\n"
        f"- IPCA Recente: {dados_ipca}"
    )
    print("[Sucesso] Dados integrados no pipeline local.\n")
    
    # Bloco 2: Montagem do payload de prompt para o Estrategista
    prompt_usuario = (
        f"Com base nas seguintes métricas coletadas da API do BACEN:\n\n{contexto_dados}\n\n"
        "E considerando o cenário de fechamento de mercado pós-eleições de outubro de 2026, realize uma "
        "auditoria detalhada para uma carteira de R$ 860.000,00 aplicada em Tesouro Selic, com retiradas mensais "
        "de R$ 11.000,00 para consumo familiar. Simule a sustentabilidade e o comportamento do fluxo de caixa "
        "pelos próximos 36 meses até o milestone da aposentadoria por idade em outubro de 2029.\n\n"
        "Gere a saída estruturada em Markdown contendo:\n"
        "1. Diagnóstico de Cenário Atual\n"
        "2. Projeção de Consumo de Capital em 3 anos\n"
        "3. Validação Matemática da Manutenção do Poder de Compra\n"
        "4. Nota técnica de Confiabilidade do Sistema."
    )
    
    # Bloco 3: Chamada através do SDK Nativo (Sem bypass ou injeção de litellm)
    print("[Executando] Enviando payload direto para os chips da Groq...")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um renomado Estrategista de Renda Fixa e Gestor de Family Office altamente conservador. Seu papel é analisar cenários de estresse patrimonial com foco em blindagem contra a inflação real."
                },
                {
                    "role": "user", 
                    "content": prompt_usuario
                }
            ],
            model=MODELO,
            temperature=0.2
        )
        
        resultado_final = chat_completion.choices[0].message.content
        
        # Gravação física do arquivo local
        with open("Relatorio_Estresse_Patrimonial.md", "w", encoding="utf-8") as f:
            f.write(resultado_final)
            
        print("\n--- Pipeline Concluído com Sucesso ---")
        print("Artefato técnico gerado com sucesso: Relatorio_Estresse_Patrimonial.md")
        
    except Exception as e:
        print(f"\n[Erro Crítico no Pipeline]: {str(e)}")
