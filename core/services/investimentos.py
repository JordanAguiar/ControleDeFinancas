from datetime import datetime
from core.models import Investimento
from core.exceptions import ValorInvalidoError, CampoObrigatorioError, DataInvalidaError
import infra


def criar_investimento(descricao: str, categoria: str, valor: str,
                       instituicao: str, data: str = None) -> Investimento:
    if not all([descricao, categoria, valor, instituicao]):
        raise CampoObrigatorioError()
    try:
        valor_float = float(valor.replace(",", "."))
    except ValueError:
        raise ValorInvalidoError("valor")

    if data:
        try:
            datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            raise DataInvalidaError(data)
    else:
        data = datetime.now().strftime("%d/%m/%Y")

    inv = Investimento(descricao=descricao, categoria=categoria,
                       valor=valor_float, instituicao=instituicao, data=data)
    infra.salvar_investimento(inv)
    return inv


def listar() -> list[Investimento]:
    return infra.buscar_investimentos()


def deletar(indice: int):
    infra.remover_investimento(indice)


def por_mes() -> dict:
    por_mes = {}
    for inv in listar():
        try:
            chave = datetime.strptime(inv.data, "%d/%m/%Y").strftime("%m/%Y")
        except (ValueError, TypeError):
            chave = "Sem data"
        por_mes[chave] = por_mes.get(chave, 0) + (inv.valor or 0)

    def parse(m):
        try:
            return datetime.strptime(m, "%m/%Y")
        except:
            return datetime.min

    return dict(sorted(por_mes.items(), key=lambda x: parse(x[0])))


def por_ano() -> dict:
    por_ano = {}
    for inv in listar():
        try:
            chave = str(datetime.strptime(inv.data, "%d/%m/%Y").year)
        except (ValueError, TypeError):
            chave = "Sem data"
        por_ano[chave] = por_ano.get(chave, 0) + (inv.valor or 0)
    return dict(sorted(por_ano.items()))


def total_mes_atual() -> float:
    hoje = datetime.now()
    return sum(
        inv.valor for inv in listar()
        if _mesmo_mes(inv.data, hoje)
    )


def _mesmo_mes(data_str: str, ref: datetime) -> bool:
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
        return dt.month == ref.month and dt.year == ref.year
    except (ValueError, TypeError):
        return False