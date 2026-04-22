from datetime import datetime
from .conexao import abrir, ARQUIVO


def adicionar_receita(descricao, categoria, valor, data=None):
    wb = abrir()
    data = data or datetime.now().strftime("%d/%m/%Y")
    if "Receitas" not in wb.sheetnames:
        wb.create_sheet("Receitas").append(
            ["Data", "Descrição", "Categoria", "Valor (R$)"])
    wb["Receitas"].append([data, descricao, categoria, float(valor)])
    wb.save(ARQUIVO)


def listar_receitas():
    wb = abrir()
    if "Receitas" not in wb.sheetnames:
        return []
    return [
        {"data": l[0], "descricao": l[1], "categoria": l[2], "valor": l[3]}
        for l in wb["Receitas"].iter_rows(min_row=2, values_only=True) if l[0]
    ]


def deletar_receita(indice):
    wb = abrir()
    wb["Receitas"].delete_rows(indice + 2)
    wb.save(ARQUIVO)