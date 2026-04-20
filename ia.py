import requests
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"  

SYSTEM_PROMPT = """Você é um assistente financeiro pessoal. 
Analise os dados financeiros do usuário e forneça:
- Resumo claro da situação financeira
- Alertas sobre dívidas críticas
- Dicas práticas de economia
- Respostas diretas e em português
Seja objetivo e use valores em reais (R$)."""


def analisar_financas(resumo: dict, pergunta: str = None) -> str:
    from config import obter_api_key
    api_key = obter_api_key() or os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Erro: chave não encontrada no arquivo .env"

    contexto = f"""
Dados financeiros atuais do usuário:
- Total gasto no período: R$ {resumo['total_gastos']:.2f}
- Total de dívidas cadastradas: R$ {resumo['total_dividas']:.2f}
- Dívidas ainda pendentes: R$ {resumo['dividas_pendentes']:.2f}
- Número de gastos registrados: {resumo['qtd_gastos']}
- Número de dívidas registradas: {resumo['qtd_dividas']}
"""

    mensagem_usuario = (
        f"{contexto}\n\nPergunta: {pergunta}"
        if pergunta
        else f"{contexto}\n\nFaça uma análise geral da minha situação financeira."
    )

    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensagem_usuario}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "Erro: a requisição demorou demais. Verifique sua conexão."
    except requests.exceptions.ConnectionError:
        return "Erro: não foi possível conectar à API. Verifique sua internet."
    except requests.exceptions.HTTPError:
        if response.status_code == 401:
            return "Erro: chave de API inválida ou expirada."