import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from dados import (adicionar_investimento, listar_investimentos,
                   deletar_investimento, investimentos_por_mes,
                   investimentos_por_ano)
from .base import (campo, criar_tabela, ROXO_ESCURO, ROXO_MEDIO, ROXO_CLARO,
                   VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED)


class InvestimentosFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        ctk.CTkLabel(self, text="Investimentos",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        # Cards totais
        frame_totais = ctk.CTkFrame(self, fg_color="transparent")
        frame_totais.pack(fill="x", padx=32, pady=(0, 12))
        frame_totais.columnconfigure(0, weight=1)
        frame_totais.columnconfigure(1, weight=1)
        frame_totais.columnconfigure(2, weight=1)

        dados_cards = [
            ("Total Investido",  "total",       VIOLETA),
            ("Este mês",         "mes",         "#1d9e75"),
            ("Categorias",       "categorias",  ROXO_CLARO),
        ]
        self.labels_inv = {}
        for i, (titulo, chave, cor) in enumerate(dados_cards):
            card = ctk.CTkFrame(frame_totais, fg_color=CARD_BG,
                                corner_radius=16, border_width=1,
                                border_color=ROXO_MEDIO)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                         text_color=TEXTO_MUTED).pack(pady=(14, 2))
            lbl = ctk.CTkLabel(card, text="R$ 0,00",
                               font=ctk.CTkFont(size=20, weight="bold"),
                               text_color=cor)
            lbl.pack(pady=(0, 14))
            self.labels_inv[chave] = lbl

        # Formulário
        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        form.pack(fill="x", padx=32, pady=(0, 12))

        self.entry_desc        = campo(form, "Descrição", 0)
        self.entry_cat         = campo(form, "Categoria", 1)
        self.entry_valor       = campo(form, "Valor (R$)", 2)
        self.entry_instituicao = campo(form, "Instituição", 3)

        # Sugestões de categoria
        ctk.CTkLabel(form, text="Sugestões:", text_color=TEXTO_MUTED,
                     font=ctk.CTkFont(size=11)
                     ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 8))

        frame_sug = ctk.CTkFrame(form, fg_color="transparent")
        frame_sug.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 8))

        for cat in ["Ações", "FII", "Tesouro Direto", "CDB", "Cripto", "Outros"]:
            ctk.CTkButton(
                frame_sug, text=cat,
                command=lambda c=cat: (
                    self.entry_cat.delete(0, "end"),
                    self.entry_cat.insert(0, c)
                ),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=VIOLETA, corner_radius=8,
                border_width=1, border_color=ROXO_MEDIO,
                width=110, height=28, font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=4)

        ctk.CTkButton(form, text="Adicionar Investimento",
                      command=self._salvar,
                      fg_color="#1d9e75", hover_color="#145f47",
                      text_color=TEXTO, corner_radius=10,
                      width=200, height=38
                      ).grid(row=5, column=1, sticky="w", padx=20, pady=(8, 20))

        # Gráficos
        frame_graficos = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        frame_graficos.pack(fill="x", padx=32, pady=(0, 12))

        frame_topo = ctk.CTkFrame(frame_graficos, fg_color="transparent")
        frame_topo.pack(fill="x", padx=16, pady=(12, 0))

        ctk.CTkLabel(frame_topo, text="Evolução dos investimentos",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VIOLETA).pack(side="left")

        self.filtro_grafico = ctk.CTkSegmentedButton(
            frame_topo,
            values=["Mensal", "Anual"],
            command=self._atualizar_graficos,
            fg_color=ROXO_ESCURO,
            selected_color=ROXO_CLARO,
            selected_hover_color=ROXO_MEDIO,
            unselected_color=ROXO_ESCURO,
            unselected_hover_color=ROXO_MEDIO,
            text_color=TEXTO,
            font=ctk.CTkFont(size=11)
        )
        self.filtro_grafico.set("Mensal")
        self.filtro_grafico.pack(side="right")

        self.frame_chart = ctk.CTkFrame(frame_graficos,
                                        fg_color="transparent", height=220)
        self.frame_chart.pack(fill="x", padx=8, pady=(8, 12))
        self.frame_chart.pack_propagate(False)

        # Botão deletar + tabela
        ctk.CTkButton(self, text="Deletar Selecionado",
                      command=self._deletar,
                      fg_color="#7f1d1d", hover_color="#991b1b",
                      text_color=TEXTO, corner_radius=10,
                      width=180, height=36).pack(anchor="e", padx=32, pady=(0, 8))

        self.tabela = criar_tabela(
            self,
            ["Data", "Descrição", "Categoria", "Valor (R$)", "Instituição"],
            [100, 200, 130, 110, 150]
        )

        self.atualizar()

    def atualizar(self):
        invs = listar_investimentos()

        total     = sum(i["valor"] or 0 for i in invs)
        from datetime import datetime
        hoje      = datetime.now()
        mes_atual = sum(
            i["valor"] or 0 for i in invs
            if self._mesmo_mes(i["data"], hoje)
        )
        cats = len(set(i["categoria"] for i in invs if i["categoria"]))

        self.labels_inv["total"].configure(     text=f"R$ {total:.2f}")
        self.labels_inv["mes"].configure(       text=f"R$ {mes_atual:.2f}")
        self.labels_inv["categorias"].configure(text=str(cats))

        self._atualizar_graficos()

        for row in self.tabela.get_children():
            self.tabela.delete(row)
        for i in invs:
            self.tabela.insert("", "end", values=(
                i["data"], i["descricao"], i["categoria"],
                f"R$ {i['valor']:.2f}", i["instituicao"]))

    def _mesmo_mes(self, data_str, hoje):
        try:
            from datetime import datetime
            dt = datetime.strptime(data_str, "%d/%m/%Y")
            return dt.month == hoje.month and dt.year == hoje.year
        except:
            return False

    def _atualizar_graficos(self, *args):
        for w in self.frame_chart.winfo_children():
            w.destroy()

        periodo = self.filtro_grafico.get()
        dados   = investimentos_por_mes() if periodo == "Mensal" else investimentos_por_ano()

        fig, axes = plt.subplots(1, 2, figsize=(10, 2.5))
        fig.patch.set_facecolor(CARD_BG)

        # Gráfico de barras — evolução
        ax1 = axes[0]
        ax1.set_facecolor(CARD_BG)
        if dados:
            labels  = list(dados.keys())
            valores = list(dados.values())
            ax1.bar(labels, valores, color="#1d9e75", width=0.5)
            ax1.set_xticks(range(len(labels)))
            ax1.set_xticklabels(labels, color=TEXTO, fontsize=7, rotation=30)
            ax1.yaxis.set_tick_params(labelcolor=TEXTO)
            ax1.tick_params(colors=TEXTO)
            for spine in ax1.spines.values():
                spine.set_edgecolor(ROXO_MEDIO)
        else:
            ax1.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                     color=TEXTO_MUTED, fontsize=11)
        ax1.set_title(f"Investimentos por {periodo.lower()}",
                      color=VIOLETA, fontsize=10, fontweight="bold")

        # Gráfico de pizza — por categoria
        ax2 = axes[1]
        ax2.set_facecolor(CARD_BG)
        invs = listar_investimentos()
        if invs:
            cats = {}
            for i in invs:
                cat = i["categoria"] or "Outros"
                cats[cat] = cats.get(cat, 0) + (i["valor"] or 0)
            cores = ["#1d9e75","#7c3aed","#a78bfa","#e67e22","#e74c3c","#c4b5fd"]
            ax2.pie(cats.values(), labels=cats.keys(),
                    colors=cores[:len(cats)], autopct="%1.1f%%",
                    textprops={"color": TEXTO, "fontsize": 8},
                    wedgeprops={"linewidth": 2, "edgecolor": CARD_BG})
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                     color=TEXTO_MUTED, fontsize=11)
        ax2.set_title("Por categoria", color=VIOLETA, fontsize=10, fontweight="bold")

        plt.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, master=self.frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _salvar(self):
        desc  = self.entry_desc.get().strip()
        cat   = self.entry_cat.get().strip()
        valor = self.entry_valor.get().strip()
        inst  = self.entry_instituicao.get().strip()

        if not desc or not cat or not valor or not inst:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            adicionar_investimento(desc, cat, float(valor.replace(",", ".")), inst)
            for e in [self.entry_desc, self.entry_cat,
                      self.entry_valor, self.entry_instituicao]:
                e.delete(0, "end")
            self.atualizar()
            messagebox.showinfo("Sucesso", "Investimento adicionado!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Ex: 500.00")

    def _deletar(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um investimento.")
            return
        if not messagebox.askyesno("Confirmar", "Deletar o investimento selecionado?"):
            return
        deletar_investimento(self.tabela.index(sel[0]))
        self.atualizar()
        messagebox.showinfo("Sucesso", "Investimento deletado!")