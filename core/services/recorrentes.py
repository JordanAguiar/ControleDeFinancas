from datetime import datetime
from core.models import GastoFixo, Parcela
from core.exceptions import ValorInvalidoError, CampoObrigatorioError
import infra
from . import gastos as gastos_service


def criar_fixo(descricao: str, categoria: str,
               valor: str, dia: str) -> GastoFixo:
    if not all([descricao, categoria, valor, dia]):
        raise CampoObrigatorioError()
    try:
        valor_float = float(valor.replace(",", "."))
        dia_int     = int(dia)
        if not 1 <= dia_int <= 31:
            raise ValueError
    except ValueError:
        raise ValorInvalidoError("valor ou dia")

    fixo = GastoFixo(descricao=descricao, categoria=categoria,
                     valor=valor_float, dia_vencimento=dia_int)
    infra.salvar_fixo(fixo)
    return fixo


def listar_fixos() -> list[GastoFixo]:
    return infra.buscar_fixos()


def deletar_fixo(indice: int):
    infra.remover_fixo(indice)


def criar_parcela(descricao: str, categoria: str, valor_total: str,
                  num_parcelas: str, data_inicio: str) -> Parcela:
    if not all([descricao, categoria, valor_total, num_parcelas]):
        raise CampoObrigatorioError()
    try:
        vt  = float(valor_total.replace(",", "."))
        num = int(num_parcelas)
        if num <= 0:
            raise ValueError
    except ValueError:
        raise ValorInvalidoError("valor ou número de parcelas")

    parcela = Parcela(
        descricao=descricao, categoria=categoria,
        valor_total=vt, num_parcelas=num,
        parcelas_pagas=0,
        valor_parcela=round(vt / num, 2),
        data_inicio=data_inicio or datetime.now().strftime("%d/%m/%Y")
    )
    infra.salvar_parcela(parcela)
    return parcela


def listar_parcelas() -> list[Parcela]:
    return infra.buscar_parcelas()


def deletar_parcela(indice: int):
    infra.remover_parcela(indice)


def lancar_fixos_mes() -> int:
    hoje    = datetime.now()
    gastos  = gastos_service.listar()
    lancados = 0

    for fixo in listar_fixos():
        if fixo.ativo != "Sim":
            continue
        dia  = fixo.dia_vencimento or 1
        data = f"{dia:02d}/{hoje.month:02d}/{hoje.year}"

        ja_lancado = any(
            g.descricao == fixo.descricao and g.data == data
            for g in gastos
        )
        if not ja_lancado:
            from core.models import Gasto
            infra.salvar_gasto(Gasto(
                descricao=fixo.descricao,
                categoria=fixo.categoria,
                valor=fixo.valor,
                data=data
            ))
            lancados += 1

    return lancados


def lancar_parcelas_mes() -> int:
    hoje     = datetime.now()
    gastos   = gastos_service.listar()
    parcelas = infra.buscar_parcelas()
    lancados = 0

    for i, p in enumerate(parcelas):
        if p.ativo != "Sim" or p.quitada:
            continue
        try:
            dt_inicio = datetime.strptime(p.data_inicio, "%d/%m/%Y")
        except (ValueError, TypeError):
            continue

        meses = (hoje.year - dt_inicio.year) * 12 + (hoje.month - dt_inicio.month)
        if meses < 0 or meses >= p.num_parcelas:
            continue

        num_atual        = meses + 1
        data_lancamento  = f"{dt_inicio.day:02d}/{hoje.month:02d}/{hoje.year}"
        desc_parcela     = f"{p.descricao} ({num_atual}/{p.num_parcelas})"

        ja_lancado = any(
            g.descricao == desc_parcela and g.data == data_lancamento
            for g in gastos
        )
        if not ja_lancado:
            from core.models import Gasto
            infra.salvar_gasto(Gasto(
                descricao=desc_parcela,
                categoria=p.categoria,
                valor=p.valor_parcela,
                data=data_lancamento
            ))
            infra.atualizar_parcelas_pagas(i, num_atual)
            lancados += 1

    return lancados