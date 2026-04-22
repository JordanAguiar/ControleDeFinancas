from datetime import datetime, timedelta
from core.models import Divida
from core.exceptions import ValorInvalidoError, CampoObrigatorioError, DataInvalidaError
import infra


def criar_divida(credor: str, descricao: str, valor_total: str,
                 valor_pago: str, vencimento: str) -> Divida:
    if not all([credor, descricao, valor_total, valor_pago, vencimento]):
        raise CampoObrigatorioError()
    try:
        vt = float(valor_total.replace(",", "."))
        vp = float(valor_pago.replace(",", "."))
    except ValueError:
        raise ValorInvalidoError("valor")

    try:
        datetime.strptime(vencimento, "%d/%m/%Y")
    except ValueError:
        raise DataInvalidaError(vencimento)

    divida = Divida(credor=credor, descricao=descricao,
                    valor_total=vt, valor_pago=vp,
                    vencimento=vencimento)
    infra.salvar_divida(divida)
    return divida


def listar() -> list[Divida]:
    return infra.buscar_dividas()


def deletar(indice: int):
    infra.remover_divida(indice)


def verificar_alertas(dias_alerta: int = 7) -> tuple[list, list]:
    hoje   = datetime.now().date()
    limite = hoje + timedelta(days=dias_alerta)
    vencidas, vencendo = [], []

    for d in listar():
        if d.status == "Quitada":
            continue
        try:
            venc = datetime.strptime(d.vencimento, "%d/%m/%Y").date()
        except (ValueError, TypeError):
            continue

        if venc < hoje:
            vencidas.append({**d.__dict__, "dias_atraso": (hoje - venc).days})
        elif venc <= limite:
            vencendo.append({**d.__dict__, "dias_restantes": (venc - hoje).days})

    return vencidas, vencendo