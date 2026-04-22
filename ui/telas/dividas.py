import customtkinter as ctk
from tkinter import messagebox
from ui.telas.base import TelaBase
from ui.components import criar_tabela, botao_primario, botao_perigo
from ui.components.formulario import campo, campo_data
from ui.theme import (FUNDO, CARD_BG, ROXO_CLARO, ROXO_MEDIO,
                      VIOLETA, LARANJA, LARANJA_HOVER, TEXTO)
from core.services import dividas as svc
from core.exceptions import FinanceiroError


class DividasTela(TelaBase):

    def _montar(self):
        ctk.CTkLabel(self, text="Dívidas",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self._credor    = campo(form, "Credor", 0)
        self._desc      = campo(form, "Descrição", 1)
        self._val_total = campo(form, "Valor Total (R$)", 2)
        self._val_pago  = campo(form, "Valor Pago (R$)", 3)
        self._venc      = campo_data(form, 4, "Vencimento", [("Hoje", 0)])

        botao_primario(form, "Adicionar Dívida", self._salvar,
                       cor=LARANJA, cor_hover=LARANJA_HOVER,
                       width=180, height=38
                       ).grid(row=5, column=1, sticky="w",
                               padx=20, pady=(8, 20))

        botao_perigo(self, "Deletar Selecionada", self._deletar,
                     width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self._tabela = criar_tabela(
            self,
            ["Credor", "Descrição", "Total", "Pago", "Vencimento", "Status"],
            [120, 180, 110, 110, 120, 100])
        self.atualizar()

    def atualizar(self):
        for r in self._tabela.get_children():
            self._tabela.delete(r)
        for d in svc.listar():
            self._tabela.insert("", "end", values=(
                d.credor, d.descricao,
                f"R$ {d.valor_total:.2f}", f"R$ {d.valor_pago:.2f}",
                d.vencimento, d.status))

    def _salvar(self):
        try:
            svc.criar_divida(
                self._credor.get(), self._desc.get(),
                self._val_total.get(), self._val_pago.get(),
                self._venc.get())
            for e in [self._credor, self._desc,
                      self._val_total, self._val_pago]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Dívida adicionada!")
        except FinanceiroError as e:
            messagebox.showerror("Erro", str(e))

    def _deletar(self):
        sel = self._tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma dívida.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar a dívida?"):
            return
        svc.deletar(self._tabela.index(sel[0]))
        self.atualizar()