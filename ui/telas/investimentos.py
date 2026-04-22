import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.telas.base import TelaBase
from ui.components import criar_tabela, botao_primario, botao_perigo
from ui.components.formulario import campo, campo_data
from ui.components import grafico
from ui.theme import (FUNDO, CARD_BG, ROXO_MEDIO, ROXO_CLARO,
                      ROXO_ESCURO, VIOLETA, VERDE, VERDE_HOVER, TEXTO, TEXTO_MUTED)
from core.services import investimentos as svc
from core.exceptions import FinanceiroError


class InvestimentosTela(TelaBase):

    def _montar(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=FUNDO, corner_radius=0)
        self.scroll.pack(fill="both", expand=True)
        s = self.scroll

        ctk.CTkLabel(s, text="Investimentos",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        # Cards
        frame_cards = ctk.CTkFrame(s, fg_color="transparent")
        frame_cards.pack(fill="x", padx=32, pady=(0, 12))
        for i in range(3):
            frame_cards.columnconfigure(i, weight=1)

        dados = [
            ("Total Investido", "_card_total",    VIOLETA),
            ("Este mês",        "_card_mes",      VERDE),
            ("Categorias",      "_card_cats",     ROXO_CLARO),
        ]
        for i, (titulo, attr, cor) in enumerate(dados):
            card = ctk.CTkFrame(frame_cards, fg_color=CARD_BG,
                                corner_radius=16, border_width=1,
                                border_color=ROXO_MEDIO)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                         text_color=TEXTO_MUTED).pack(pady=(14, 2))
            lbl = ctk.CTkLabel(card, text="—",
                               font=ctk.CTkFont(size=20, weight="bold"),
                               text_color=cor)
            lbl.pack(pady=(0, 14))
            setattr(self, attr, lbl)

        # Formulário
        form = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))
        self._desc  = campo(form, "Descrição", 0)
        self._cat   = campo(form, "Categoria", 1)
        self._valor = campo(form, "Valor (R$)", 2)
        self._inst  = campo(form, "Instituição", 3)
        self._data  = campo_data(form, 4)

        # Sugestões
        ctk.CTkLabel(form, text="Sugestões:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=5, column=0, sticky="w", padx=20, pady=(0, 8))
        frame_sug = ctk.CTkFrame(form, fg_color="transparent")
        frame_sug.grid(row=5, column=1, sticky="w", padx=20, pady=(0, 8))
        for cat in ["Ações", "FII", "Tesouro Direto", "CDB", "Cripto", "Outros"]:
            ctk.CTkButton(
                frame_sug, text=cat,
                command=lambda c=cat: (
                    self._cat.delete(0, "end"),
                    self._cat.insert(0, c)),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=6,
                border_width=1, border_color=ROXO_MEDIO,
                width=110, height=28,
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=4)

        botao_primario(form, "Adicionar Investimento", self._salvar,
                       cor=VERDE, cor_hover=VERDE_HOVER,
                       width=200, height=38
                       ).grid(row=6, column=1, sticky="w",
                               padx=20, pady=(8, 20))

        # Gráficos
        frame_g = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=16)
        frame_g.pack(fill="x", padx=32, pady=(0, 12))
        frame_topo = ctk.CTkFrame(frame_g, fg_color="transparent")
        frame_topo.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(frame_topo, text="Evolução dos investimentos",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VIOLETA).pack(side="left")
        self._filtro_g = ctk.CTkSegmentedButton(
            frame_topo, values=["Mensal", "Anual"],
            command=self._atualizar_graficos,
            fg_color=ROXO_ESCURO, selected_color=ROXO_CLARO,
            selected_hover_color=ROXO_MEDIO,
            unselected_color=ROXO_ESCURO,
            unselected_hover_color=ROXO_MEDIO,
            text_color=TEXTO, font=ctk.CTkFont(size=11))
        self._filtro_g.set("Mensal")
        self._filtro_g.pack(side="right")
        self._frame_chart = ctk.CTkFrame(frame_g, fg_color="transparent", height=220)
        self._frame_chart.pack(fill="x", padx=8, pady=(8, 12))
        self._frame_chart.pack_propagate(False)

        botao_perigo(s, "Deletar Selecionado", self._deletar,
                     width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self._tabela = criar_tabela(
            s,
            ["Data", "Descrição", "Categoria", "Valor (R$)", "Instituição"],
            [100, 200, 130, 110, 150])
        self.atualizar()

    def atualizar(self):
        invs  = svc.listar()
        total = sum(i.valor for i in invs)
        mes   = svc.total_mes_atual()
        cats  = len(set(i.categoria for i in invs if i.categoria))

        self._card_total.configure(text=f"R$ {total:.2f}")
        self._card_mes.configure(  text=f"R$ {mes:.2f}")
        self._card_cats.configure( text=str(cats))

        for r in self._tabela.get_children():
            self._tabela.delete(r)
        for i in invs:
            self._tabela.insert("", "end", values=(
                i.data, i.descricao, i.categoria,
                f"R$ {i.valor:.2f}", i.instituicao))

        self._atualizar_graficos()

    def _atualizar_graficos(self, *args):
        periodo = self._filtro_g.get()
        dados   = svc.por_mes() if periodo == "Mensal" else svc.por_ano()
        grafico.barras(self._frame_chart, dados, cor=VERDE)

    def _salvar(self):
        try:
            svc.criar_investimento(
                self._desc.get(), self._cat.get(),
                self._valor.get(), self._inst.get(),
                self._data.get())
            for e in [self._desc, self._cat, self._valor, self._inst]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Investimento adicionado!")
        except FinanceiroError as e:
            messagebox.showerror("Erro", str(e))

    def _deletar(self):
        sel = self._tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um investimento.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o investimento?"):
            return
        svc.deletar(self._tabela.index(sel[0]))
        self.atualizar()