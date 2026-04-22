import customtkinter as ctk
from tkinter import messagebox
from ui.telas.base import TelaBase
from ui.components import criar_tabela, botao_primario, botao_perigo
from ui.components.formulario import campo, campo_data
from ui.theme import (FUNDO, CARD_BG, ROXO_MEDIO, ROXO_CLARO,
                      VIOLETA, VERDE, VERDE_HOVER, TEXTO, TEXTO_MUTED)
from core.services import receitas as svc
from core.exceptions import FinanceiroError


class ReceitasTela(TelaBase):

    def _montar(self):
        ctk.CTkLabel(self, text="Receitas",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self._desc  = campo(form, "Descrição", 0)
        self._cat   = campo(form, "Categoria", 1)
        self._valor = campo(form, "Valor (R$)", 2)
        self._data  = campo_data(form, 3)

        # Sugestões
        ctk.CTkLabel(form, text="Sugestões:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 8))
        frame_sug = ctk.CTkFrame(form, fg_color="transparent")
        frame_sug.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 8))
        for cat in ["Salário", "Freelancer", "Investimento", "Presente", "Outros"]:
            ctk.CTkButton(
                frame_sug, text=cat,
                command=lambda c=cat: (
                    self._cat.delete(0, "end"),
                    self._cat.insert(0, c)),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=8,
                border_width=1, border_color=ROXO_MEDIO,
                width=100, height=28,
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=4)

        botao_primario(form, "Adicionar Receita", self._salvar,
                       cor=VERDE, cor_hover=VERDE_HOVER,
                       width=180, height=38
                       ).grid(row=5, column=1, sticky="w",
                               padx=20, pady=(8, 20))

        botao_perigo(self, "Deletar Selecionada", self._deletar,
                     width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self._tabela = criar_tabela(
            self,
            ["Data", "Descrição", "Categoria", "Valor (R$)"],
            [110, 260, 160, 120])
        self.atualizar()

    def atualizar(self):
        for r in self._tabela.get_children():
            self._tabela.delete(r)
        for r in svc.listar():
            self._tabela.insert("", "end", values=(
                r.data, r.descricao, r.categoria, f"R$ {r.valor:.2f}"))

    def _salvar(self):
        try:
            svc.criar_receita(self._desc.get(), self._cat.get(),
                              self._valor.get(), self._data.get())
            for e in [self._desc, self._cat, self._valor]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Receita adicionada!")
        except FinanceiroError as e:
            messagebox.showerror("Erro", str(e))

    def _deletar(self):
        sel = self._tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma receita.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar a receita?"):
            return
        svc.deletar(self._tabela.index(sel[0]))
        self.atualizar()