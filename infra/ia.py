import requests
from core.exceptions import APIError
from infra.config import obter_api_key

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """Você é um assistente financeiro pessoal.
Analise os dados financeiros do usuário e forneça:
- Resumo claro da situação financeira
- Alertas sobre dívidas críticas
- Dicas práticas de economia
- Respostas diretas e em português
Seja objetivo e use valores em reais (R$)."""


def analisar(resumo: dict, pergunta: str = None) -> str:
    api_key = obter_api_key()

    if not api_key:
        raise APIError("Chave de API não configurada.")

    contexto = f"""
Dados financeiros atuais:
- Gastos do mês:       R$ {resumo.get('total_gastos', 0):.2f}
- Receitas do mês:     R$ {resumo.get('total_receitas', 0):.2f}
- Saldo do mês:        R$ {resumo.get('saldo', 0):.2f}
- Total de dívidas:    R$ {resumo.get('total_dividas', 0):.2f}
- Dívidas pendentes:   R$ {resumo.get('dividas_pendentes', 0):.2f}
- Gastos registrados:  {resumo.get('qtd_gastos', 0)}
- Dívidas registradas: {resumo.get('qtd_dividas', 0)}
"""

    mensagem = (f"{contexto}\n\nPergunta: {pergunta}"
                if pergunta else
                f"{contexto}\n\nFaça uma análise geral da minha situação financeira.")

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model":       "llama-3.3-70b-versatile",
                "messages":    [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": mensagem}
                ],
                "temperature": 0.7,
                "max_tokens":  1024
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        raise APIError("Requisição expirou. Verifique sua conexão.")
    except requests.exceptions.ConnectionError:
        raise APIError("Sem conexão com a internet.")
    except requests.exceptions.HTTPError:
        if response.status_code == 401:
            raise APIError("Chave de API inválida ou expirada.")
        raise APIError(f"Erro HTTP {response.status_code}.")
    except Exception as e:
        raise APIError(str(e))