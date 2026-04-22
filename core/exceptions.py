class FinanceiroError(Exception):
    """Erro base do sistema financeiro."""
    pass


class ValorInvalidoError(FinanceiroError):
    """Valor numérico inválido."""
    def __init__(self, campo: str = "valor"):
        super().__init__(f"Valor inválido para o campo '{campo}'. Use números. Ex: 49.90")


class DataInvalidaError(FinanceiroError):
    """Data em formato inválido."""
    def __init__(self, valor: str = ""):
        super().__init__(f"Data inválida: '{valor}'. Use o formato dd/mm/aaaa.")


class CampoObrigatorioError(FinanceiroError):
    """Campo obrigatório não preenchido."""
    def __init__(self, campo: str = ""):
        msg = f"O campo '{campo}' é obrigatório." if campo else "Preencha todos os campos obrigatórios."
        super().__init__(msg)


class RegistroNaoEncontradoError(FinanceiroError):
    """Registro não encontrado."""
    def __init__(self, tipo: str = "Registro"):
        super().__init__(f"{tipo} não encontrado.")


class APIError(FinanceiroError):
    """Erro na comunicação com a API de IA."""
    def __init__(self, detalhe: str = ""):
        super().__init__(f"Erro na API de IA: {detalhe}")


class ConfiguracaoError(FinanceiroError):
    """Erro de configuração do sistema."""
    def __init__(self, detalhe: str = ""):
        super().__init__(f"Erro de configuração: {detalhe}")