from datetime import datetime
from .conexao import abrir, ARQUIVO


def adicionar_gasto(descricao, categoria, valor, data=None):
    wb = abrir()
    data = data or datetime.now().strftime("%d/%m/%Y")
    wb["Gastos"].append([data, descricao, categoria, float(valor)])
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


def editar_gasto(indice, descricao, categoria, valor, data):
    wb = abrir()
    ws = wb["Gastos"]
    row = indice + 2
    ws.cell(row=row, column=1, value=data)
    ws.cell(row=row, column=2, value=descricao)
    ws.cell(row=row, column=3, value=categoria)
    ws.cell(row=row, column=4, value=float(valor))
    wb.save(ARQUIVO)


def filtrar_gastos(categoria=None, data_inicio=None, data_fim=None):
    resultado = []
    for g in listar_gastos():
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


def gastos_por_semana():
    por_semana = {}
    for g in listar_gastos():
        try:
            dt    = datetime.strptime(g["data"], "%d/%m/%Y")
            chave = f"Sem {dt.strftime('%W/%Y')}"
        except (ValueError, TypeError):
            chave = "Sem data"
        por_semana[chave] = por_semana.get(chave, 0) + (g["valor"] or 0)

    def parse(s):
        try:
            p = s.replace("Sem ", "").split("/")
            return datetime.strptime(f"{p[0]} {p[1]}", "%W %Y")
        except:
            return datetime.min

    return dict(sorted(por_semana.items(), key=lambda x: parse(x[0])))


def gastos_por_mes():
    por_mes = {}
    for g in listar_gastos():
        try:
            chave = datetime.strptime(g["data"], "%d/%m/%Y").strftime("%m/%Y")
        except (ValueError, TypeError):
            chave = "Sem data"
        por_mes[chave] = por_mes.get(chave, 0) + (g["valor"] or 0)

    def parse(m):
        try:
            return datetime.strptime(m, "%m/%Y")
        except:
            return datetime.min

    return dict(sorted(por_mes.items(), key=lambda x: parse(x[0])))


def total_semana_atual():
    hoje   = datetime.now().date()
    inicio = hoje - __import__("datetime").timedelta(days=hoje.weekday())
    total  = 0.0
    for g in listar_gastos():
        try:
            dt = datetime.strptime(g["data"], "%d/%m/%Y").date()
            if inicio <= dt <= hoje:
                total += g["valor"] or 0
        except (ValueError, TypeError):
            continue
    return total


def total_mes_atual():
    hoje  = datetime.now()
    total = 0.0
    for g in listar_gastos():
        try:
            dt = datetime.strptime(g["data"], "%d/%m/%Y")
            if dt.month == hoje.month and dt.year == hoje.year:
                total += g["valor"] or 0
        except (ValueError, TypeError):
            continue
    return total


# ── Gastos Fixos ─────────────────────────────────────────────

def adicionar_fixo(descricao, categoria, valor, dia_vencimento):
    """Cadastra um gasto fixo recorrente."""
    wb = abrir()
    if "Fixos" not in wb.sheetnames:
        wb.create_sheet("Fixos").append(
            ["Descrição", "Categoria", "Valor (R$)", "Dia Vencimento", "Ativo"])
    wb["Fixos"].append([descricao, categoria, float(valor), int(dia_vencimento), "Sim"])
    wb.save(ARQUIVO)


def listar_fixos():
    wb = abrir()
    if "Fixos" not in wb.sheetnames:
        return []
    return [
        {"descricao": l[0], "categoria": l[1], "valor": l[2],
         "dia_vencimento": l[3], "ativo": l[4]}
        for l in wb["Fixos"].iter_rows(min_row=2, values_only=True) if l[0]
    ]


def deletar_fixo(indice):
    wb = abrir()
    wb["Fixos"].delete_rows(indice + 2)
    wb.save(ARQUIVO)


def editar_fixo(indice, descricao, categoria, valor, dia_vencimento, ativo):
    wb = abrir()
    ws = wb["Fixos"]
    row = indice + 2
    ws.cell(row=row, column=1, value=descricao)
    ws.cell(row=row, column=2, value=categoria)
    ws.cell(row=row, column=3, value=float(valor))
    ws.cell(row=row, column=4, value=int(dia_vencimento))
    ws.cell(row=row, column=5, value=ativo)
    wb.save(ARQUIVO)


def lancar_fixos_mes_atual():
    """Lança todos os fixos ativos como gasto no mês atual se ainda não lançados."""
    from datetime import datetime
    hoje  = datetime.now()
    gastos_existentes = listar_gastos()

    lancados = 0
    for fixo in listar_fixos():
        if fixo["ativo"] != "Sim":
            continue

        dia  = fixo["dia_vencimento"] or 1
        data = f"{dia:02d}/{hoje.month:02d}/{hoje.year}"

        # Verifica se já foi lançado este mês
        ja_lancado = any(
            g["descricao"] == fixo["descricao"] and
            g["data"] == data
            for g in gastos_existentes
        )

        if not ja_lancado:
            adicionar_gasto(fixo["descricao"], fixo["categoria"],
                            fixo["valor"], data)
            lancados += 1

    return lancados


# ── Parcelas ─────────────────────────────────────────────────

def adicionar_parcela(descricao, categoria, valor_total,
                      num_parcelas, data_inicio):
    """Cadastra uma compra parcelada."""
    wb = abrir()
    if "Parcelas" not in wb.sheetnames:
        wb.create_sheet("Parcelas").append([
            "Descrição", "Categoria", "Valor Total (R$)",
            "Nº Parcelas", "Parcelas Pagas", "Valor Parcela (R$)",
            "Data Início", "Ativo"
        ])

    valor_parcela = float(valor_total) / int(num_parcelas)
    wb["Parcelas"].append([
        descricao, categoria, float(valor_total),
        int(num_parcelas), 0,
        round(valor_parcela, 2),
        data_inicio, "Sim"
    ])
    wb.save(ARQUIVO)


def listar_parcelas():
    wb = abrir()
    if "Parcelas" not in wb.sheetnames:
        return []
    return [
        {
            "descricao":      l[0],
            "categoria":      l[1],
            "valor_total":    l[2],
            "num_parcelas":   l[3],
            "parcelas_pagas": l[4],
            "valor_parcela":  l[5],
            "data_inicio":    l[6],
            "ativo":          l[7],
        }
        for l in wb["Parcelas"].iter_rows(min_row=2, values_only=True) if l[0]
    ]


def deletar_parcela(indice):
    wb = abrir()
    wb["Parcelas"].delete_rows(indice + 2)
    wb.save(ARQUIVO)


def lancar_parcelas_mes_atual():
    """Lança a parcela do mês atual para cada parcelamento ativo."""
    from datetime import datetime
    hoje  = datetime.now()
    gastos_existentes = listar_gastos()
    wb    = abrir()
    ws    = wb["Parcelas"] if "Parcelas" in wb.sheetnames else None
    if not ws:
        return 0

    lancados = 0
    for i, parcela in enumerate(listar_parcelas()):
        if parcela["ativo"] != "Sim":
            continue
        if parcela["parcelas_pagas"] >= parcela["num_parcelas"]:
            continue

        try:
            dt_inicio = datetime.strptime(parcela["data_inicio"], "%d/%m/%Y")
        except (ValueError, TypeError):
            continue

        # Calcula mês atual da parcela
        meses_passados = (hoje.year - dt_inicio.year) * 12 + (hoje.month - dt_inicio.month)
        if meses_passados < 0 or meses_passados >= parcela["num_parcelas"]:
            continue

        num_atual = meses_passados + 1
        data_lancamento = f"{dt_inicio.day:02d}/{hoje.month:02d}/{hoje.year}"
        desc_parcela = f"{parcela['descricao']} ({num_atual}/{parcela['num_parcelas']})"

        ja_lancado = any(
            g["descricao"] == desc_parcela and g["data"] == data_lancamento
            for g in gastos_existentes
        )

        if not ja_lancado:
            adicionar_gasto(parcela["categoria"], parcela["categoria"],
                            parcela["valor_parcela"], data_lancamento)
            adicionar_gasto(desc_parcela, parcela["categoria"],
                            parcela["valor_parcela"], data_lancamento)

            # Atualiza parcelas pagas
            ws.cell(row=i + 2, column=5, value=num_atual)
            lancados += 1

    wb.save(ARQUIVO)
    return lancados