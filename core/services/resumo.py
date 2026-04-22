from datetime import datetime
from core.models import Resumo
from . import gastos as gs
from . import receitas as rs
from . import dividas as ds
from . import investimentos as inv_s
import infra


def calcular() -> Resumo:
    hoje      = datetime.now()
    gastos    = gs.listar()
    receitas  = rs.listar()
    dividas   = ds.listar()
    invs      = inv_s.listar()

    def mesmo_mes(data_str):
        try:
            dt = datetime.strptime(data_str, "%d/%m/%Y")
            return dt.month == hoje.month and dt.year == hoje.year
        except (ValueError, TypeError):
            return False

    total_gastos   = sum(g.valor for g in gastos   if mesmo_mes(g.data))
    total_receitas = sum(r.valor for r in receitas if mesmo_mes(r.data))
    total_dividas  = sum(d.valor_total for d in dividas)
    pendentes      = sum(d.valor_pendente for d in dividas if d.status == "Pendente")

    return Resumo(
        total_gastos      = total_gastos,
        total_receitas    = total_receitas,
        total_dividas     = total_dividas,
        dividas_pendentes = pendentes,
        saldo             = total_receitas - total_gastos,
        qtd_gastos        = len(gastos),
        qtd_dividas       = len(dividas),
        qtd_receitas      = len(receitas),
        qtd_investimentos = len(invs),
    )


def buscar_meta() -> float:
    return infra.buscar_meta()


def salvar_meta(valor: float):
    infra.salvar_meta(valor)