from datetime import datetime, timedelta
from .conexao import abrir, ARQUIVO


def adicionar_divida(credor, descricao, valor_total, valor_pago, vencimento):
    wb = abrir()
    restante = float(valor_total) - float(valor_pago)
    status = "Quitada" if restante <= 0 else "Pendente"
    wb["Dividas"].append([credor, descricao, float(valor_total), float(valor_pago), vencimento, status])
    wb.save(ARQUIVO)


def listar_dividas():
    ws = abrir()["Dividas"]
    return [
        {"credor": l[0], "descricao": l[1], "valor_total": l[2],
         "valor_pago": l[3], "vencimento": l[4], "status": l[5]}
        for l in ws.iter_rows(min_row=2, values_only=True) if l[0]
    ]


def deletar_divida(indice):
    wb = abrir()
    wb["Dividas"].delete_rows(indice + 2)
    wb.save(ARQUIVO)


def verificar_dividas_vencendo(dias_alerta=7):
    hoje   = datetime.now().date()
    limite = hoje + timedelta(days=dias_alerta)
    vencidas, vencendo = [], []

    for d in listar_dividas():
        if d["status"] == "Quitada":
            continue
        try:
            venc = datetime.strptime(d["vencimento"], "%d/%m/%Y").date()
        except (ValueError, TypeError):
            continue
        if venc < hoje:
            d["dias_atraso"] = (hoje - venc).days
            vencidas.append(d)
        elif venc <= limite:
            d["dias_restantes"] = (venc - hoje).days
            vencendo.append(d)

    return vencidas, vencendo