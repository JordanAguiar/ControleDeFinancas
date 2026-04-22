import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from dados import (adicionar_gasto, listar_gastos, deletar_gasto,
                   filtrar_gastos, gastos_por_semana, gastos_por_mes,
                   total_semana_atual, total_mes_atual,
                   adicionar_fixo, listar_fixos, deletar_fixo, editar_fixo,
                   lancar_fixos_mes_atual, adicionar_parcela, listar_parcelas,
                   deletar_parcela, lancar_parcelas_mes_atual)
from .base import campo, criar_tabela
from .base import ROXO_ESCURO, ROXO_MEDIO, ROXO_CLARO, VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED

try:
    from .data_entry import CampoData
except ImportError:
    CampoData = None


def _campo_data(parent):
    """Cria campo de data inline sem depender do componente externo."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    parent.columnconfigure(0, weight=0, minsize=180)
    parent.columnconfigure(1, weight=1)

    ctk.CTkLabel(frame, text="Data", text_color=TEXTO_MUTED,
                 font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))

    entry = ctk.CTkEntry(frame, placeholder_text="dd/mm/aaaa",
                         height=36, corner_radius=8, width=140,
                         fg_color=ROXO_ESCURO, text_color=TEXTO,
                         border_color=ROXO_CLARO)
    entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
    entry.pack(side="left", padx=(0, 8))

    for label, dias in [("Hoje", 0), ("Ontem", -1), ("Anteontem", -2)]:
        def set_data(d=dias, e=entry):
            from datetime import timedelta
            e.delete(0, "end")
            e.insert(0, (datetime.now() + timedelta(days=d)).strftime("%d/%m/%Y"))
        ctk.CTkButton(frame, text=label, command=set_data,
                      fg_color="transparent", hover_color=ROXO_MEDIO,
                      text_color=VIOLETA, corner_radius=6,
                      border_width=1, border_color=ROXO_MEDIO,
                      width=80, height=28,
                      font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 4))

    return frame, entry


class GastosFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=FUNDO, corner_radius=0)
        self.scroll.pack(fill="both", expand=True)
        s = self.scroll

        # ── Título + botão lançar ────────────────────────────
        frame_titulo = ctk.CTkFrame(s, fg_color="transparent")
        frame_titulo.pack(fill="x", padx=32, pady=(28, 12))

        ctk.CTkLabel(frame_titulo, text="Gastos",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(side="left")

        ctk.CTkButton(frame_titulo,
                      text="Lançar fixos e parcelas do mês",
                      command=self._lancar_recorrentes,
                      fg_color=ROXO_MEDIO, hover_color=ROXO_CLARO,
                      text_color=TEXTO, corner_radius=10,
                      height=36).pack(side="right")

        # ── Cards semana / mês ───────────────────────────────
        frame_totais = ctk.CTkFrame(s, fg_color="transparent")
        frame_totais.pack(fill="x", padx=32, pady=(0, 12))
        frame_totais.columnconfigure(0, weight=1)
        frame_totais.columnconfigure(1, weight=1)

        for col, titulo, attr in [
            (0, "Esta semana", "label_semana"),
            (1, "Este mês",    "label_mes")
        ]:
            card = ctk.CTkFrame(frame_totais, fg_color=CARD_BG,
                                corner_radius=16, border_width=1,
                                border_color=ROXO_MEDIO)
            card.grid(row=0, column=col,
                      padx=(0, 8) if col == 0 else (8, 0),
                      sticky="nsew")
            ctk.CTkLabel(card, text=titulo,
                         font=ctk.CTkFont(size=11),
                         text_color=TEXTO_MUTED).pack(pady=(14, 2))
            lbl = ctk.CTkLabel(card, text="R$ 0,00",
                               font=ctk.CTkFont(size=22, weight="bold"),
                               text_color=VIOLETA)
            lbl.pack(pady=(0, 14))
            setattr(self, attr, lbl)

        # ── Formulário de gasto ──────────────────────────────
        ctk.CTkLabel(s, text="Registrar Gasto",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(8, 4))

        form = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self.entry_desc  = campo(form, "Descrição", 0)
        self.entry_cat   = campo(form, "Categoria", 1)
        self.entry_valor = campo(form, "Valor (R$)", 2)

        # Campo data com atalhos
        ctk.CTkLabel(form, text="Data", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=12)
                     ).grid(row=3, column=0, sticky="w", padx=20, pady=6)

        frame_data = ctk.CTkFrame(form, fg_color="transparent")
        frame_data.grid(row=3, column=1, sticky="ew", padx=(0, 20), pady=6)

        self.entry_data = ctk.CTkEntry(
            frame_data, placeholder_text="dd/mm/aaaa",
            height=36, corner_radius=8, width=140,
            fg_color=ROXO_ESCURO, text_color=TEXTO,
            border_color=ROXO_CLARO)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_data.pack(side="left", padx=(0, 8))

        for label, dias in [("Hoje", 0), ("Ontem", -1), ("Anteontem", -2)]:
            ctk.CTkButton(
                frame_data, text=label,
                command=lambda d=dias: self._set_data_gasto(d),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=6,
                border_width=1, border_color=ROXO_MEDIO,
                width=80, height=28,
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(form, text="Adicionar Gasto",
                      command=self._salvar,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=38
                      ).grid(row=4, column=1, sticky="w",
                             padx=20, pady=(8, 20))

        # ── Filtros ──────────────────────────────────────────
        frame_f = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_f.pack(fill="x", padx=32, pady=(0, 12))
        frame_f.columnconfigure(1, weight=1)
        frame_f.columnconfigure(2, weight=1)
        frame_f.columnconfigure(3, weight=1)

        ctk.CTkLabel(frame_f, text="Filtrar:",
                     text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=12)
                     ).grid(row=0, column=0, padx=16, pady=12, sticky="w")

        self.filtro_cat = ctk.CTkEntry(frame_f, placeholder_text="Categoria",
                                       height=34, corner_radius=8,
                                       fg_color=ROXO_ESCURO, text_color=TEXTO,
                                       border_color=ROXO_CLARO)
        self.filtro_cat.grid(row=0, column=1, padx=8, pady=12, sticky="ew")

        self.filtro_di = ctk.CTkEntry(frame_f,
                                      placeholder_text="Data início (dd/mm/aaaa)",
                                      height=34, corner_radius=8,
                                      fg_color=ROXO_ESCURO, text_color=TEXTO,
                                      border_color=ROXO_CLARO)
        self.filtro_di.grid(row=0, column=2, padx=8, pady=12, sticky="ew")

        self.filtro_df = ctk.CTkEntry(frame_f,
                                      placeholder_text="Data fim (dd/mm/aaaa)",
                                      height=34, corner_radius=8,
                                      fg_color=ROXO_ESCURO, text_color=TEXTO,
                                      border_color=ROXO_CLARO)
        self.filtro_df.grid(row=0, column=3, padx=8, pady=12, sticky="ew")

        frame_btns_f = ctk.CTkFrame(frame_f, fg_color="transparent")
        frame_btns_f.grid(row=0, column=4, padx=8, pady=12)

        ctk.CTkButton(frame_btns_f, text="Filtrar",
                      command=self._filtrar,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=8,
                      width=90, height=34).pack(side="left", padx=(0, 6))

        ctk.CTkButton(frame_btns_f, text="Limpar",
                      command=self.atualizar,
                      fg_color="transparent", hover_color=ROXO_MEDIO,
                      text_color=TEXTO_MUTED, corner_radius=8,
                      border_width=1, border_color=ROXO_MEDIO,
                      width=90, height=34).pack(side="left")

        ctk.CTkButton(s, text="Deletar Selecionado",
                      command=self._deletar,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        # ── Tabela de gastos ─────────────────────────────────
        ctk.CTkLabel(s, text="Lançamentos",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(8, 4))

        frame_tab = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_tab.pack(fill="x", padx=32, pady=(0, 12))
        self.tabela = criar_tabela(frame_tab,
                                   ["Data", "Descrição", "Categoria", "Valor (R$)"],
                                   [110, 260, 160, 120])

        # ── Gráfico de evolução ──────────────────────────────
        frame_grafico = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_grafico.pack(fill="x", padx=32, pady=(0, 12))

        frame_topo_g = ctk.CTkFrame(frame_grafico, fg_color="transparent")
        frame_topo_g.pack(fill="x", padx=16, pady=(12, 0))

        ctk.CTkLabel(frame_topo_g, text="Evolução de gastos",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VIOLETA).pack(side="left")

        self.filtro_periodo = ctk.CTkSegmentedButton(
            frame_topo_g,
            values=["Semanal", "Mensal"],
            command=self._atualizar_grafico,
            fg_color=ROXO_ESCURO,
            selected_color=ROXO_CLARO,
            selected_hover_color=ROXO_MEDIO,
            unselected_color=ROXO_ESCURO,
            unselected_hover_color=ROXO_MEDIO,
            text_color=TEXTO,
            font=ctk.CTkFont(size=11))
        self.filtro_periodo.set("Mensal")
        self.filtro_periodo.pack(side="right")

        self.frame_chart = ctk.CTkFrame(frame_grafico,
                                        fg_color="transparent", height=220)
        self.frame_chart.pack(fill="x", padx=8, pady=(8, 12))
        self.frame_chart.pack_propagate(False)

        # ── Gastos Fixos ─────────────────────────────────────
        ctk.CTkLabel(s, text="Gastos Fixos",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(16, 4))

        form_fixo = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form_fixo.pack(fill="x", padx=32, pady=(0, 12))

        self.fixo_desc = campo(form_fixo, "Descrição", 0)
        self.fixo_cat  = campo(form_fixo, "Categoria", 1)
        self.fixo_val  = campo(form_fixo, "Valor (R$)", 2)
        self.fixo_dia  = campo(form_fixo, "Dia de vencimento", 3)

        # Sugestões de fixos
        ctk.CTkLabel(form_fixo, text="Sugestões:",
                     text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 8))

        frame_sug_fixo = ctk.CTkFrame(form_fixo, fg_color="transparent")
        frame_sug_fixo.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 8))

        for nome in ["Aluguel", "Água", "Luz", "Internet", "Condomínio"]:
            ctk.CTkButton(
                frame_sug_fixo, text=nome,
                command=lambda n=nome: (
                    self.fixo_desc.delete(0, "end"),
                    self.fixo_desc.insert(0, n),
                    self.fixo_cat.delete(0, "end"),
                    self.fixo_cat.insert(0, "Fixo")
                ),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=6,
                border_width=1, border_color=ROXO_MEDIO,
                width=100, height=26,
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(form_fixo, text="Adicionar Fixo",
                      command=self._salvar_fixo,
                      fg_color="#1d9e75", hover_color="#145f47",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=38
                      ).grid(row=5, column=1, sticky="w",
                             padx=20, pady=(8, 20))

        ctk.CTkButton(s, text="Deletar Fixo Selecionado",
                      command=self._deletar_fixo,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=200, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        frame_tab_fixo = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_tab_fixo.pack(fill="x", padx=32, pady=(0, 12))
        self.tabela_fixos = criar_tabela(
            frame_tab_fixo,
            ["Descrição", "Categoria", "Valor (R$)", "Dia Venc.", "Ativo"],
            [200, 150, 120, 100, 80]
        )

        # ── Parcelas ─────────────────────────────────────────
        ctk.CTkLabel(s, text="Compras Parceladas",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(16, 4))

        form_parcela = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form_parcela.pack(fill="x", padx=32, pady=(0, 12))

        self.parc_desc  = campo(form_parcela, "Descrição", 0)
        self.parc_cat   = campo(form_parcela, "Categoria", 1)
        self.parc_total = campo(form_parcela, "Valor Total (R$)", 2)
        self.parc_num   = campo(form_parcela, "Nº de Parcelas", 3)

        ctk.CTkLabel(form_parcela, text="Data 1ª parcela",
                     text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=12)
                     ).grid(row=4, column=0, sticky="w", padx=20, pady=6)

        frame_data_p = ctk.CTkFrame(form_parcela, fg_color="transparent")
        frame_data_p.grid(row=4, column=1, sticky="ew", padx=(0, 20), pady=6)

        self.parc_data = ctk.CTkEntry(
            frame_data_p, placeholder_text="dd/mm/aaaa",
            height=36, corner_radius=8, width=140,
            fg_color=ROXO_ESCURO, text_color=TEXTO,
            border_color=ROXO_CLARO)
        self.parc_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.parc_data.pack(side="left", padx=(0, 8))

        for label, dias in [("Hoje", 0), ("Ontem", -1)]:
            ctk.CTkButton(
                frame_data_p, text=label,
                command=lambda d=dias: self._set_data_parcela(d),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=6,
                border_width=1, border_color=ROXO_MEDIO,
                width=80, height=28,
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(form_parcela, text="Adicionar Parcelamento",
                      command=self._salvar_parcela,
                      fg_color="#e67e22", hover_color="#b35c00",
                      text_color=TEXTO, corner_radius=10,
                      width=200, height=38
                      ).grid(row=5, column=1, sticky="w",
                             padx=20, pady=(8, 20))

        ctk.CTkButton(s, text="Deletar Parcela Selecionada",
                      command=self._deletar_parcela,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=220, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        frame_tab_parc = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_tab_parc.pack(fill="x", padx=32, pady=(0, 24))
        self.tabela_parcelas = criar_tabela(
            frame_tab_parc,
            ["Descrição", "Categoria", "Total", "Parcelas", "Pagas",
             "Valor/Parc.", "1ª Parcela", "Status"],
            [160, 110, 90, 80, 70, 100, 100, 80]
        )

        self.atualizar()

    # ── Helpers de data ──────────────────────────────────────
    def _set_data_gasto(self, dias):
        from datetime import timedelta
        self.entry_data.delete(0, "end")
        self.entry_data.insert(
            0, (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y"))

    def _set_data_parcela(self, dias):
        from datetime import timedelta
        self.parc_data.delete(0, "end")
        self.parc_data.insert(
            0, (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y"))

    # ── Atualizar ────────────────────────────────────────────
    def atualizar(self):
        self.label_semana.configure(text=f"R$ {total_semana_atual():.2f}")
        self.label_mes.configure(   text=f"R$ {total_mes_atual():.2f}")

        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for g in listar_gastos():
            self.tabela.insert("", "end", values=(
                g["data"], g["descricao"], g["categoria"],
                f"R$ {g['valor']:.2f}"))

        for row in self.tabela_fixos.get_children():
            self.tabela_fixos.delete(row)
        for f in listar_fixos():
            self.tabela_fixos.insert("", "end", values=(
                f["descricao"], f["categoria"],
                f"R$ {f['valor']:.2f}",
                f["dia_vencimento"], f["ativo"]))

        for row in self.tabela_parcelas.get_children():
            self.tabela_parcelas.delete(row)
        for p in listar_parcelas():
            restantes = p["num_parcelas"] - p["parcelas_pagas"]
            status    = "Quitado" if restantes <= 0 else f"{restantes} restantes"
            self.tabela_parcelas.insert("", "end", values=(
                p["descricao"], p["categoria"],
                f"R$ {p['valor_total']:.2f}",
                p["num_parcelas"], p["parcelas_pagas"],
                f"R$ {p['valor_parcela']:.2f}",
                p["data_inicio"], status))

        self._atualizar_grafico()

    # ── Gastos ───────────────────────────────────────────────
    def _salvar(self):
        desc  = self.entry_desc.get().strip()
        cat   = self.entry_cat.get().strip()
        valor = self.entry_valor.get().strip()
        data  = self.entry_data.get().strip()

        if not desc or not cat or not valor:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_gasto(desc, cat, float(valor.replace(",", ".")), data)
            for e in [self.entry_desc, self.entry_cat, self.entry_valor]:
                e.delete(0, "end")
            self.entry_data.delete(0, "end")
            self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
            self.atualizar()
            messagebox.showinfo("Sucesso", "Gasto adicionado!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Ex: 49.90")

    def _filtrar(self):
        cat = self.filtro_cat.get().strip() or None
        di  = self.filtro_di.get().strip() or None
        df  = self.filtro_df.get().strip() or None
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for g in filtrar_gastos(categoria=cat, data_inicio=di, data_fim=df):
            self.tabela.insert("", "end", values=(
                g["data"], g["descricao"], g["categoria"],
                f"R$ {g['valor']:.2f}"))

    def _deletar(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um gasto.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o gasto selecionado?"):
            return
        deletar_gasto(self.tabela.index(sel[0]))
        self.atualizar()
        messagebox.showinfo("Sucesso", "Gasto deletado!")

    # ── Fixos ────────────────────────────────────────────────
    def _salvar_fixo(self):
        desc = self.fixo_desc.get().strip()
        cat  = self.fixo_cat.get().strip()
        val  = self.fixo_val.get().strip()
        dia  = self.fixo_dia.get().strip()

        if not desc or not cat or not val or not dia:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_fixo(desc, cat, float(val.replace(",", ".")), int(dia))
            for e in [self.fixo_desc, self.fixo_cat,
                      self.fixo_val, self.fixo_dia]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Gasto fixo cadastrado!")
        except ValueError:
            messagebox.showerror("Erro", "Valor ou dia inválido.")

    def _deletar_fixo(self):
        sel = self.tabela_fixos.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um gasto fixo.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o gasto fixo?"):
            return
        deletar_fixo(self.tabela_fixos.index(sel[0]))
        self.atualizar()
        messagebox.showinfo("Sucesso", "Gasto fixo deletado!")

    # ── Parcelas ─────────────────────────────────────────────
    def _salvar_parcela(self):
        desc  = self.parc_desc.get().strip()
        cat   = self.parc_cat.get().strip()
        total = self.parc_total.get().strip()
        num   = self.parc_num.get().strip()
        data  = self.parc_data.get().strip()

        if not desc or not cat or not total or not num:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_parcela(desc, cat,
                              float(total.replace(",", ".")),
                              int(num), data)
            for e in [self.parc_desc, self.parc_cat,
                      self.parc_total, self.parc_num]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso",
                                f"Parcelamento de {num}x cadastrado!\n"
                                f"Clique em 'Lançar fixos e parcelas do mês' "
                                f"para registrar a parcela atual.")
        except ValueError:
            messagebox.showerror("Erro", "Valor ou número de parcelas inválido.")

    def _deletar_parcela(self):
        sel = self.tabela_parcelas.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma parcela.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o parcelamento?"):
            return
        deletar_parcela(self.tabela_parcelas.index(sel[0]))
        self.atualizar()
        messagebox.showinfo("Sucesso", "Parcelamento deletado!")

    # ── Lançar recorrentes ───────────────────────────────────
    def _lancar_recorrentes(self):
        fixos    = lancar_fixos_mes_atual()
        parcelas = lancar_parcelas_mes_atual()
        total    = fixos + parcelas

        if total == 0:
            messagebox.showinfo("Sem novidades",
                                "Todos os fixos e parcelas já foram lançados este mês.")
        else:
            messagebox.showinfo("Lançamentos realizados",
                                f"{fixos} gasto(s) fixo(s) e "
                                f"{parcelas} parcela(s) lançados com sucesso!")
        self.atualizar()

    # ── Gráfico ──────────────────────────────────────────────
    def _atualizar_grafico(self, *args):
        for w in self.frame_chart.winfo_children():
            w.destroy()

        periodo = self.filtro_periodo.get()
        dados   = gastos_por_semana() if periodo == "Semanal" else gastos_por_mes()

        fig, ax = plt.subplots(figsize=(10, 2.2))
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)

        if dados and len(dados) > 0:
            labels  = list(dados.keys())
            valores = list(dados.values())
            x       = range(len(labels))

            ax.plot(x, valores, color=VIOLETA, linewidth=2.5, zorder=3)
            ax.scatter(x, valores, color=ROXO_CLARO, s=50, zorder=4)
            ax.fill_between(x, valores, alpha=0.15, color=ROXO_CLARO)

            for i, v in enumerate(valores):
                ax.annotate(f"R${v:.0f}", xy=(i, v),
                            xytext=(0, 8), textcoords="offset points",
                            ha="center", fontsize=7, color=VIOLETA)

            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, color=TEXTO, fontsize=7, rotation=30)
            ax.yaxis.set_tick_params(labelcolor=TEXTO)
            ax.tick_params(colors=TEXTO)
            ax.set_xlim(-0.5, len(labels) - 0.5)
            for spine in ax.spines.values():
                spine.set_edgecolor(ROXO_MEDIO)
        else:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    color=TEXTO_MUTED, fontsize=11)

        plt.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)