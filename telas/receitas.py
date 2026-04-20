import customtkinter as ctk
from tkinter import messagebox
from dados import adicionar_receita, listar_receitas, deletar_receita
from .base import campo, criar_tabela, ROXO_ESCURO, ROXO_MEDIO, ROXO_CLARO, VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED


class ReceitasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        ctk.CTkLabel(self, text="Registrar Receita",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self.entry_desc  = campo(form, "Descrição", 0)
        self.entry_cat   = campo(form, "Categoria", 1)
        self.entry_valor = campo(form, "Valor (R$)", 2)

        # Sugestões de categoria
        ctk.CTkLabel(form, text="Sugestões:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 8))

        frame_sugestoes = ctk.CTkFrame(form, fg_color="transparent")
        frame_sugestoes.grid(row=3, column=1, sticky="w", padx=20, pady=(0, 8))

        for cat in ["Salário", "Freelancer", "Investimento", "Presente", "Outros"]:
            ctk.CTkButton(
                frame_sugestoes, text=cat,
                command=lambda c=cat: (self.entry_cat.delete(0, "end"), self.entry_cat.insert(0, c)),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=8,
                border_width=1, border_color=ROXO_MEDIO,
                width=100, height=28, font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=4)

        ctk.CTkButton(form, text="Adicionar Receita", command=self._salvar,
                      fg_color="#1d9e75", hover_color="#145f47",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=38
                      ).grid(row=4, column=1, sticky="w", padx=20, pady=(8, 20))

        ctk.CTkButton(self, text="Deletar Selecionada", command=self._deletar,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self.tabela = criar_tabela(self, ["Data", "Descrição", "Categoria", "Valor (R$)"],
                                   [110, 260, 160, 120])
        self.atualizar()

    def atualizar(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for r in listar_receitas():
            self.tabela.insert("", "end", values=(
                r["data"], r["descricao"], r["categoria"], f"R$ {r['valor']:.2f}"))

    def _salvar(self):
        desc  = self.entry_desc.get().strip()
        cat   = self.entry_cat.get().strip()
        valor = self.entry_valor.get().strip()
        if not desc or not cat or not valor:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_receita(desc, cat, float(valor.replace(",", ".")))
            for e in [self.entry_desc, self.entry_cat, self.entry_valor]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Receita adicionada!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Ex: 3500.00")

    def _deletar(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma receita.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar a receita selecionada?"):
            return
        deletar_receita(self.tabela.index(sel[0]))
        self.atualizar()
        messagebox.showinfo("Sucesso", "Receita deletada!")