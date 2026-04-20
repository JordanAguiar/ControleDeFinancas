import customtkinter as ctk
from tkinter import messagebox
from dados import adicionar_divida, listar_dividas, deletar_divida
from .base import campo, criar_tabela, ROXO_MEDIO, ROXO_CLARO, VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED


class DividasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        ctk.CTkLabel(self, text="Registrar Dívida",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self.entry_credor    = campo(form, "Credor", 0)
        self.entry_desc      = campo(form, "Descrição", 1)
        self.entry_val_total = campo(form, "Valor Total (R$)", 2)
        self.entry_val_pago  = campo(form, "Valor Pago (R$)", 3)
        self.entry_venc      = campo(form, "Vencimento (dd/mm/aaaa)", 4)

        ctk.CTkButton(form, text="Adicionar Dívida", command=self._salvar,
                      fg_color="#e67e22", hover_color="#b35c00",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=38
                      ).grid(row=5, column=1, sticky="w", padx=20, pady=(8, 20))

        ctk.CTkButton(self, text="Deletar Selecionada", command=self._deletar,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self.tabela = criar_tabela(
            self,
            ["Credor", "Descrição", "Total", "Pago", "Vencimento", "Status"],
            [120, 180, 110, 110, 120, 100]
        )
        self.atualizar()

    def atualizar(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for d in listar_dividas():
            self.tabela.insert("", "end", values=(
                d["credor"], d["descricao"],
                f"R$ {d['valor_total']:.2f}", f"R$ {d['valor_pago']:.2f}",
                d["vencimento"], d["status"]))

    def _salvar(self):
        credor = self.entry_credor.get().strip()
        desc   = self.entry_desc.get().strip()
        total  = self.entry_val_total.get().strip()
        pago   = self.entry_val_pago.get().strip()
        venc   = self.entry_venc.get().strip()

        if not all([credor, desc, total, pago, venc]):
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_divida(credor, desc,
                             float(total.replace(",", ".")),
                             float(pago.replace(",", ".")), venc)
            for e in [self.entry_credor, self.entry_desc,
                      self.entry_val_total, self.entry_val_pago, self.entry_venc]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Dívida adicionada!")
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos. Ex: 1500.00")

    def _deletar(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma dívida.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar a dívida selecionada?"):
            return
        deletar_divida(self.tabela.index(sel[0]))
        self.atualizar()
        messagebox.showinfo("Sucesso", "Dívida deletada!")