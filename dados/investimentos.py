from datetime import datetime
from .conexao import abrir, ARQUIVO


def adicionar_investimento(descricao, categoria, valor, instituicao, data=None):
    wb = abrir()
    data = data or datetime.now().strftime("%d/%m/%Y")
    if "Investimentos" not in wb.sheetnames:
        wb.create_sheet("Investimentos").append(
            ["Data", "Descrição", "Categoria", "Valor (R$)", "Instituição"])
    wb["Investimentos"].append([data, descricao, categoria, float(valor), instituicao])
    wb.save(ARQUIVO)


def listar_investimentos():
    wb = abrir()
    if "Investimentos" not in wb.sheetnames:
        return []
    return [
        {"data": l[0], "descricao": l[1], "categoria": l[2],
         "valor": l[3], "instituicao": l[4]}
        for l in wb["Investimentos"].iter_rows(min_row=2, values_only=True) if l[0]
    ]


def deletar_investimento(indice):
    wb = abrir()
    wb["Investimentos"].delete_rows(indice + 2)
    wb.save(ARQUIVO)


def investimentos_por_mes():
    por_mes = {}
    for inv in listar_investimentos():
        try:
            chave = datetime.strptime(inv["data"], "%d/%m/%Y").strftime("%m/%Y")
        except (ValueError, TypeError):
            chave = "Sem data"
        por_mes[chave] = por_mes.get(chave, 0) + (inv["valor"] or 0)

    def parse(m):
        try:
            return datetime.strptime(m, "%m/%Y")
        except:
            return datetime.min

    return dict(sorted(por_mes.items(), key=lambda x: parse(x[0])))


def investimentos_por_ano():
    por_ano = {}
    for inv in listar_investimentos():
        try:
            chave = str(datetime.strptime(inv["data"], "%d/%m/%Y").year)
        except (ValueError, TypeError):
            chave = "Sem data"
        por_ano[chave] = por_ano.get(chave, 0) + (inv["valor"] or 0)
    return dict(sorted(por_ano.items()))