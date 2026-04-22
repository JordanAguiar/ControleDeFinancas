from datetime import datetime, timedelta
from core.models import Gasto
from core.exceptions import ValorInvalidoError, CampoObrigatorioError, DataInvalidaError
import infra


def criar_gasto(descricao: str, categoria: str, valor: str, data: str = None) -> Gasto:
    if not descricao or not categoria or not valor:
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

    gasto = Gasto(descricao=descricao, categoria=categoria,
                  valor=valor_float, data=data)
    infra.salvar_gasto(gasto)
    return gasto


def listar() -> list[Gasto]:
    return infra.buscar_gastos()


def deletar(indice: int):
    infra.remover_gasto(indice)


def filtrar(categoria: str = None,
            data_inicio: str = None,
            data_fim: str = None) -> list[Gasto]:
    resultado = []
    for g in listar():
        if categoria and categoria.lower() not in (g.categoria or "").lower():
            continue
        if data_inicio or data_fim:
            try:
                dt = datetime.strptime(g.data, "%d/%m/%Y")
                if data_inicio and dt < datetime.strptime(data_inicio, "%d/%m/%Y"):
                    continue
                if data_fim and dt > datetime.strptime(data_fim, "%d/%m/%Y"):
                    continue
            except (ValueError, TypeError):
                continue
        resultado.append(g)
    return resultado


def por_semana() -> dict:
    por_semana = {}
    for g in listar():
        try:
            dt    = datetime.strptime(g.data, "%d/%m/%Y")
            chave = f"Sem {dt.strftime('%W/%Y')}"
        except (ValueError, TypeError):
            chave = "Sem data"
        por_semana[chave] = por_semana.get(chave, 0) + (g.valor or 0)

    def parse(s):
        try:
            p = s.replace("Sem ", "").split("/")
            return datetime.strptime(f"{p[0]} {p[1]}", "%W %Y")
        except:
            return datetime.min

    return dict(sorted(por_semana.items(), key=lambda x: parse(x[0])))


def por_mes() -> dict:
    por_mes = {}
    for g in listar():
        try:
            chave = datetime.strptime(g.data, "%d/%m/%Y").strftime("%m/%Y")
        except (ValueError, TypeError):
            chave = "Sem data"
        por_mes[chave] = por_mes.get(chave, 0) + (g.valor or 0)

    def parse(m):
        try:
            return datetime.strptime(m, "%m/%Y")
        except:
            return datetime.min

    return dict(sorted(por_mes.items(), key=lambda x: parse(x[0])))


def total_semana_atual() -> float:
    hoje   = datetime.now().date()
    inicio = hoje - timedelta(days=hoje.weekday())
    return sum(
        g.valor for g in listar()
        if _parse_data(g.data) and inicio <= _parse_data(g.data) <= hoje
    )


def total_mes_atual() -> float:
    hoje = datetime.now()
    return sum(
        g.valor for g in listar()
        if _mesmo_mes(g.data, hoje)
    )


def _parse_data(data_str: str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def _mesmo_mes(data_str: str, ref: datetime) -> bool:
    dt = _parse_data(data_str)
    if not dt:
        return False
    return dt.month == ref.month and dt.year == ref.year