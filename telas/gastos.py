import customtkinter as ctk
from tkinter import messagebox
from dados import adicionar_gasto, listar_gastos, deletar_gasto, filtrar_gastos
from .base import campo, criar_tabela, ROXO_ESCURO, ROXO_MEDIO, ROXO_CLARO, VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED


class GastosFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        ctk.CTkLabel(self, text="Registrar Gasto",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self.entry_desc  = campo(form, "Descrição", 0)
        self.entry_cat   = campo(form, "Categoria", 1)
        self.entry_valor = campo(form, "Valor (R$)", 2)

        ctk.CTkButton(form, text="Adicionar Gasto", command=self._salvar,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=38
                      ).grid(row=3, column=1, sticky="w", padx=20, pady=(8, 20))

        # Filtros
        frame_f = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        frame_f.pack(fill="x", padx=32, pady=(0, 12))

        ctk.CTkLabel(frame_f, text="Filtrar:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=16, pady=12)

        self.filtro_cat = ctk.CTkEntry(frame_f, placeholder_text="Categoria",
                                       width=160, height=34, corner_radius=8,
                                       fg_color=ROXO_ESCURO, text_color=TEXTO,
                                       border_color=ROXO_CLARO)
        self.filtro_cat.grid(row=0, column=1, padx=8)

        self.filtro_di = ctk.CTkEntry(frame_f, placeholder_text="Data início (dd/mm/aaaa)",
                                      width=190, height=34, corner_radius=8,
                                      fg_color=ROXO_ESCURO, text_color=TEXTO,
                                      border_color=ROXO_CLARO)
        self.filtro_di.grid(row=0, column=2, padx=8)

        self.filtro_df = ctk.CTkEntry(frame_f, placeholder_text="Data fim (dd/mm/aaaa)",
                                      width=190, height=34, corner_radius=8,
                                      fg_color=ROXO_ESCURO, text_color=TEXTO,
                                      border_color=ROXO_CLARO)
        self.filtro_df.grid(row=0, column=3, padx=8)

        ctk.CTkButton(frame_f, text="Filtrar", command=self._filtrar,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=8, width=90, height=34
                      ).grid(row=0, column=4, padx=8)

        ctk.CTkButton(frame_f, text="Limpar", command=self.atualizar,
                      fg_color="transparent", hover_color=ROXO_MEDIO,
                      text_color=TEXTO_MUTED, corner_radius=8,
                      border_width=1, border_color=ROXO_MEDIO,
                      width=90, height=34).grid(row=0, column=5, padx=8)

        ctk.CTkButton(self, text="Deletar Selecionado", command=self._deletar,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self.tabela = criar_tabela(self, ["Data", "Descrição", "Categoria", "Valor (R$)"],
                                   [110, 260, 160, 120])
        self.atualizar()

    def atualizar(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for g in listar_gastos():
            self.tabela.insert("", "end", values=(
                g["data"], g["descricao"], g["categoria"], f"R$ {g['valor']:.2f}"))

    def _filtrar(self):
        cat = self.filtro_cat.get().strip() or None
        di  = self.filtro_di.get().strip() or None
        df  = self.filtro_df.get().strip() or None
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for g in filtrar_gastos(categoria=cat, data_inicio=di, data_fim=df):
            self.tabela.insert("", "end", values=(
                g["data"], g["descricao"], g["categoria"], f"R$ {g['valor']:.2f}"))

    def _salvar(self):
        desc, cat, valor = self.entry_desc.get().strip(), self.entry_cat.get().strip(), self.entry_valor.get().strip()
        if not desc or not cat or not valor:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_gasto(desc, cat, float(valor.replace(",", ".")))
            for e in [self.entry_desc, self.entry_cat, self.entry_valor]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Gasto adicionado!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Ex: 49.90")

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