import customtkinter as ctk
from tkinter import messagebox
from ui.telas.base import TelaBase
from ui.components import criar_tabela, botao_perigo, botao_outline, botao_primario
from ui.components.formulario import campo, campo_data
from ui.components import grafico
from ui.theme import (FUNDO, CARD_BG, ROXO_ESCURO, ROXO_MEDIO,
                      ROXO_CLARO, VIOLETA, VERDE, VERDE_HOVER,
                      TEXTO, TEXTO_MUTED)
from core.services import gastos as svc
from core.services import recorrentes as rec_svc
from core.exceptions import FinanceiroError


class GastosTela(TelaBase):

    def _montar(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=FUNDO, corner_radius=0)
        self.scroll.pack(fill="both", expand=True)
        s = self.scroll

        # Título + botão lançar
        frame_titulo = ctk.CTkFrame(s, fg_color="transparent")
        frame_titulo.pack(fill="x", padx=32, pady=(28, 12))
        ctk.CTkLabel(frame_titulo, text="Gastos",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(side="left")
        botao_primario(frame_titulo, "Lançar fixos e parcelas do mês",
                       self._lancar_recorrentes,
                       cor=ROXO_MEDIO, cor_hover=ROXO_CLARO,
                       height=36).pack(side="right")

        # Cards semana / mês
        frame_totais = ctk.CTkFrame(s, fg_color="transparent")
        frame_totais.pack(fill="x", padx=32, pady=(0, 12))
        frame_totais.columnconfigure(0, weight=1)
        frame_totais.columnconfigure(1, weight=1)

        for col, titulo, attr in [
            (0, "Esta semana", "_label_semana"),
            (1, "Este mês",    "_label_mes")
        ]:
            card = ctk.CTkFrame(frame_totais, fg_color=CARD_BG,
                                corner_radius=16, border_width=1,
                                border_color=ROXO_MEDIO)
            card.grid(row=0, column=col,
                      padx=(0,8) if col==0 else (8,0), sticky="nsew")
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                         text_color=TEXTO_MUTED).pack(pady=(14, 2))
            lbl = ctk.CTkLabel(card, text="R$ 0,00",
                               font=ctk.CTkFont(size=22, weight="bold"),
                               text_color=VIOLETA)
            lbl.pack(pady=(0, 14))
            setattr(self, attr, lbl)

        # Formulário
        ctk.CTkLabel(s, text="Registrar Gasto",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(8, 4))

        form = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self._desc  = campo(form, "Descrição", 0)
        self._cat   = campo(form, "Categoria", 1)
        self._valor = campo(form, "Valor (R$)", 2)
        self._data  = campo_data(form, 3)

        botao_primario(form, "Adicionar Gasto", self._salvar,
                       width=180, height=38
                       ).grid(row=4, column=1, sticky="w",
                               padx=20, pady=(8, 20))

        # Filtros
        frame_f = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_f.pack(fill="x", padx=32, pady=(0, 12))
        frame_f.columnconfigure(1, weight=1)
        frame_f.columnconfigure(2, weight=1)
        frame_f.columnconfigure(3, weight=1)

        ctk.CTkLabel(frame_f, text="Filtrar:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=12)
                     ).grid(row=0, column=0, padx=16, pady=12, sticky="w")

        self._filtro_cat = ctk.CTkEntry(
            frame_f, placeholder_text="Categoria",
            height=34, corner_radius=8,
            fg_color=ROXO_ESCURO, text_color=TEXTO,
            border_color=ROXO_CLARO)
        self._filtro_cat.grid(row=0, column=1, padx=8, pady=12, sticky="ew")

        self._filtro_di = ctk.CTkEntry(
            frame_f, placeholder_text="Data início (dd/mm/aaaa)",
            height=34, corner_radius=8,
            fg_color=ROXO_ESCURO, text_color=TEXTO,
            border_color=ROXO_CLARO)
        self._filtro_di.grid(row=0, column=2, padx=8, pady=12, sticky="ew")

        self._filtro_df = ctk.CTkEntry(
            frame_f, placeholder_text="Data fim (dd/mm/aaaa)",
            height=34, corner_radius=8,
            fg_color=ROXO_ESCURO, text_color=TEXTO,
            border_color=ROXO_CLARO)
        self._filtro_df.grid(row=0, column=3, padx=8, pady=12, sticky="ew")

        frame_btns = ctk.CTkFrame(frame_f, fg_color="transparent")
        frame_btns.grid(row=0, column=4, padx=8, pady=12)
        botao_primario(frame_btns, "Filtrar", self._filtrar,
                       width=90, height=34).pack(side="left", padx=(0,6))
        botao_outline(frame_btns, "Limpar", self.atualizar,
                      width=90, height=34).pack(side="left")

        botao_perigo(s, "Deletar Selecionado", self._deletar,
                     width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        # Tabela
        ctk.CTkLabel(s, text="Lançamentos",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(8, 4))
        frame_tab = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_tab.pack(fill="x", padx=32, pady=(0, 12))
        self._tabela = criar_tabela(frame_tab,
                                    ["Data", "Descrição", "Categoria", "Valor (R$)"],
                                    [110, 260, 160, 120])

        # Gráfico
        frame_g = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_g.pack(fill="x", padx=32, pady=(0, 12))
        frame_topo = ctk.CTkFrame(frame_g, fg_color="transparent")
        frame_topo.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(frame_topo, text="Evolução de gastos",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VIOLETA).pack(side="left")
        self._filtro_periodo = ctk.CTkSegmentedButton(
            frame_topo, values=["Semanal", "Mensal"],
            command=self._atualizar_grafico,
            fg_color=ROXO_ESCURO, selected_color=ROXO_CLARO,
            selected_hover_color=ROXO_MEDIO,
            unselected_color=ROXO_ESCURO,
            unselected_hover_color=ROXO_MEDIO,
            text_color=TEXTO, font=ctk.CTkFont(size=11))
        self._filtro_periodo.set("Mensal")
        self._filtro_periodo.pack(side="right")
        self._frame_chart = ctk.CTkFrame(frame_g, fg_color="transparent", height=220)
        self._frame_chart.pack(fill="x", padx=8, pady=(8, 12))
        self._frame_chart.pack_propagate(False)

        # Gastos fixos
        ctk.CTkLabel(s, text="Gastos Fixos",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(16, 4))
        form_f = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form_f.pack(fill="x", padx=32, pady=(0, 12))
        self._fixo_desc = campo(form_f, "Descrição", 0)
        self._fixo_cat  = campo(form_f, "Categoria", 1)
        self._fixo_val  = campo(form_f, "Valor (R$)", 2)
        self._fixo_dia  = campo(form_f, "Dia de vencimento", 3)

        ctk.CTkLabel(form_f, text="Sugestões:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 8))
        frame_sug = ctk.CTkFrame(form_f, fg_color="transparent")
        frame_sug.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 8))
        for nome in ["Aluguel", "Água", "Luz", "Internet", "Condomínio"]:
            ctk.CTkButton(
                frame_sug, text=nome,
                command=lambda n=nome: (
                    self._fixo_desc.delete(0, "end"),
                    self._fixo_desc.insert(0, n),
                    self._fixo_cat.delete(0, "end"),
                    self._fixo_cat.insert(0, "Fixo")),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=6,
                border_width=1, border_color=ROXO_MEDIO,
                width=100, height=26,
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=(0, 6))

        botao_primario(form_f, "Adicionar Fixo", self._salvar_fixo,
                       cor=VERDE, cor_hover=VERDE_HOVER,
                       width=180, height=38
                       ).grid(row=5, column=1, sticky="w",
                               padx=20, pady=(8, 20))

        botao_perigo(s, "Deletar Fixo", self._deletar_fixo,
                     width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        frame_tab_f = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_tab_f.pack(fill="x", padx=32, pady=(0, 12))
        self._tabela_fixos = criar_tabela(
            frame_tab_f,
            ["Descrição", "Categoria", "Valor (R$)", "Dia Venc.", "Ativo"],
            [200, 150, 120, 100, 80])

        # Parcelas
        ctk.CTkLabel(s, text="Compras Parceladas",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(16, 4))
        form_p = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form_p.pack(fill="x", padx=32, pady=(0, 12))
        self._parc_desc  = campo(form_p, "Descrição", 0)
        self._parc_cat   = campo(form_p, "Categoria", 1)
        self._parc_total = campo(form_p, "Valor Total (R$)", 2)
        self._parc_num   = campo(form_p, "Nº de Parcelas", 3)
        self._parc_data  = campo_data(form_p, 4, "Data 1ª parcela",
                                      [("Hoje", 0), ("Ontem", -1)])

        botao_primario(form_p, "Adicionar Parcelamento", self._salvar_parcela,
                       cor="#e67e22", cor_hover="#b35c00",
                       width=200, height=38
                       ).grid(row=5, column=1, sticky="w",
                               padx=20, pady=(8, 20))

        botao_perigo(s, "Deletar Parcela", self._deletar_parcela,
                     width=200, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        frame_tab_p = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_tab_p.pack(fill="x", padx=32, pady=(0, 24))
        self._tabela_parcelas = criar_tabela(
            frame_tab_p,
            ["Descrição", "Categoria", "Total", "Parcelas",
             "Pagas", "Valor/Parc.", "1ª Parcela", "Status"],
            [160, 110, 90, 80, 70, 100, 100, 90])

        self.atualizar()

    def atualizar(self):
        self._label_semana.configure(text=f"R$ {svc.total_semana_atual():.2f}")
        self._label_mes.configure(   text=f"R$ {svc.total_mes_atual():.2f}")
        self._recarregar_tabela()
        self._recarregar_fixos()
        self._recarregar_parcelas()
        self._atualizar_grafico()

    def _recarregar_tabela(self):
        for r in self._tabela.get_children():
            self._tabela.delete(r)
        for g in svc.listar():
            self._tabela.insert("", "end", values=(
                g.data, g.descricao, g.categoria, f"R$ {g.valor:.2f}"))

    def _recarregar_fixos(self):
        for r in self._tabela_fixos.get_children():
            self._tabela_fixos.delete(r)
        for f in rec_svc.listar_fixos():
            self._tabela_fixos.insert("", "end", values=(
                f.descricao, f.categoria,
                f"R$ {f.valor:.2f}", f.dia_vencimento, f.ativo))

    def _recarregar_parcelas(self):
        for r in self._tabela_parcelas.get_children():
            self._tabela_parcelas.delete(r)
        for p in rec_svc.listar_parcelas():
            self._tabela_parcelas.insert("", "end", values=(
                p.descricao, p.categoria,
                f"R$ {p.valor_total:.2f}", p.num_parcelas,
                p.parcelas_pagas, f"R$ {p.valor_parcela:.2f}",
                p.data_inicio, p.status))

    def _filtrar(self):
        cat = self._filtro_cat.get().strip() or None
        di  = self._filtro_di.get().strip() or None
        df  = self._filtro_df.get().strip() or None
        for r in self._tabela.get_children():
            self._tabela.delete(r)
        for g in svc.filtrar(categoria=cat, data_inicio=di, data_fim=df):
            self._tabela.insert("", "end", values=(
                g.data, g.descricao, g.categoria, f"R$ {g.valor:.2f}"))

    def _salvar(self):
        try:
            svc.criar_gasto(self._desc.get(), self._cat.get(),
                            self._valor.get(), self._data.get())
            for e in [self._desc, self._cat, self._valor]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Gasto adicionado!")
        except FinanceiroError as e:
            messagebox.showerror("Erro", str(e))

    def _deletar(self):
        sel = self._tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um gasto.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o gasto selecionado?"):
            return
        svc.deletar(self._tabela.index(sel[0]))
        self.atualizar()

    def _salvar_fixo(self):
        try:
            rec_svc.criar_fixo(self._fixo_desc.get(), self._fixo_cat.get(),
                               self._fixo_val.get(), self._fixo_dia.get())
            for e in [self._fixo_desc, self._fixo_cat,
                      self._fixo_val, self._fixo_dia]:
                e.delete(0, "end")
            self._recarregar_fixos()
            messagebox.showinfo("Sucesso", "Gasto fixo cadastrado!")
        except FinanceiroError as e:
            messagebox.showerror("Erro", str(e))

    def _deletar_fixo(self):
        sel = self._tabela_fixos.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um gasto fixo.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o gasto fixo?"):
            return
        rec_svc.deletar_fixo(self._tabela_fixos.index(sel[0]))
        self._recarregar_fixos()

    def _salvar_parcela(self):
        try:
            rec_svc.criar_parcela(
                self._parc_desc.get(), self._parc_cat.get(),
                self._parc_total.get(), self._parc_num.get(),
                self._parc_data.get())
            for e in [self._parc_desc, self._parc_cat,
                      self._parc_total, self._parc_num]:
                e.delete(0, "end")
            self._recarregar_parcelas()
            messagebox.showinfo("Sucesso", "Parcelamento cadastrado!")
        except FinanceiroError as e:
            messagebox.showerror("Erro", str(e))

    def _deletar_parcela(self):
        sel = self._tabela_parcelas.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma parcela.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o parcelamento?"):
            return
        rec_svc.deletar_parcela(self._tabela_parcelas.index(sel[0]))
        self._recarregar_parcelas()

    def _lancar_recorrentes(self):
        fixos    = rec_svc.lancar_fixos_mes()
        parcelas = rec_svc.lancar_parcelas_mes()
        if fixos + parcelas == 0:
            messagebox.showinfo("Sem novidades",
                                "Tudo já foi lançado este mês.")
        else:
            messagebox.showinfo("Sucesso",
                                f"{fixos} fixo(s) e {parcelas} parcela(s) lançados!")
        self.atualizar()

    def _atualizar_grafico(self, *args):
        periodo = self._filtro_periodo.get()
        dados   = svc.por_semana() if periodo == "Semanal" else svc.por_mes()
        grafico.linha(self._frame_chart, dados)