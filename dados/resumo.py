from datetime import datetime
from .gastos import listar_gastos
from .receitas import listar_receitas
from .dividas import listar_dividas
from .conexao import abrir, ARQUIVO


def resumo_financeiro():
    from datetime import datetime
    from .gastos   import listar_gastos
    from .receitas import listar_receitas
    from .dividas  import listar_dividas

    gastos   = listar_gastos()
    dividas  = listar_dividas()
    receitas = listar_receitas()

    hoje = datetime.now()

    # Apenas mês atual
    gastos_mes = sum(
        g["valor"] for g in gastos
        if g["valor"] and _mesmo_mes(g["data"], hoje)
    )
    receitas_mes = sum(
        r["valor"] for r in receitas
        if r["valor"] and _mesmo_mes(r["data"], hoje)
    )

    total_dividas = sum(d["valor_total"] for d in dividas if d["valor_total"])
    pendentes     = sum(
        d["valor_total"] - d["valor_pago"]
        for d in dividas if d["status"] == "Pendente"
    )

    return {
        "total_gastos":      gastos_mes,
        "total_receitas":    receitas_mes,
        "total_dividas":     total_dividas,
        "dividas_pendentes": pendentes,
        "saldo":             receitas_mes - gastos_mes,
        "qtd_gastos":        len(gastos),
        "qtd_dividas":       len(dividas),
        "qtd_receitas":      len(receitas),
    }


def _mesmo_mes(data_str, hoje):
    from datetime import datetime
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
        return dt.month == hoje.month and dt.year == hoje.year
    except (ValueError, TypeError):
        return False


def salvar_meta(valor_meta):
    wb = abrir()
    if "Meta" not in wb.sheetnames:
        wb.create_sheet("Meta").append(["Meta Mensal (R$)", "Data Definida"])
    ws = wb["Meta"]
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.value = None
    ws.cell(row=2, column=1, value=float(valor_meta))
    ws.cell(row=2, column=2, value=datetime.now().strftime("%d/%m/%Y"))
    wb.save(ARQUIVO)


def carregar_meta():
    wb = abrir()
    if "Meta" not in wb.sheetnames:
        return 0.0
    valor = wb["Meta"].cell(row=2, column=1).value
    return float(valor) if valor else 0.0