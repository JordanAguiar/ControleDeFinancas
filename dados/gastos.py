from datetime import datetime
from .conexao import abrir, ARQUIVO


def adicionar_gasto(descricao, categoria, valor):
    wb = abrir()
    wb["Gastos"].append([datetime.now().strftime("%d/%m/%Y"), descricao, categoria, float(valor)])
    wb.save(ARQUIVO)


def listar_gastos():
    ws = abrir()["Gastos"]
    return [
        {"data": l[0], "descricao": l[1], "categoria": l[2], "valor": l[3]}
        for l in ws.iter_rows(min_row=2, values_only=True) if l[0]
    ]


def deletar_gasto(indice):
    wb = abrir()
    wb["Gastos"].delete_rows(indice + 2)
    wb.save(ARQUIVO)


def filtrar_gastos(categoria=None, data_inicio=None, data_fim=None):
    gastos = listar_gastos()
    resultado = []
    for g in gastos:
        if categoria and categoria.lower() not in (g["categoria"] or "").lower():
            continue
        if data_inicio or data_fim:
            try:
                data = datetime.strptime(g["data"], "%d/%m/%Y")
                if data_inicio and data < datetime.strptime(data_inicio, "%d/%m/%Y"):
                    continue
                if data_fim and data > datetime.strptime(data_fim, "%d/%m/%Y"):
                    continue
            except (ValueError, TypeError):
                continue
        resultado.append(g)
    return resultado


def gastos_por_data():
    por_data = {}
    for g in listar_gastos():
        data = g["data"] or "Sem data"
        por_data[data] = por_data.get(data, 0) + (g["valor"] or 0)

    def parse(d):
        try:
            return datetime.strptime(d, "%d/%m/%Y")
        except:
            return datetime.min

    return dict(sorted(por_data.items(), key=lambda x: parse(x[0])))