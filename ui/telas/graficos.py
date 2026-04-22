import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.telas.base import TelaBase
from ui.theme import (FUNDO, CARD_BG, ROXO_ESCURO, ROXO_MEDIO,
                      ROXO_CLARO, VIOLETA, TEXTO, TEXTO_MUTED)
from core.services import gastos as gs
from core.services import dividas as ds
from core.services import investimentos as inv_s


class GraficosTela(TelaBase):

    def _montar(self):
        ctk.CTkLabel(self, text="Gráficos e Dashboards",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 16))

        self._frame_graficos = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_graficos.pack(fill="both", expand=True, padx=32, pady=(0, 20))

    def atualizar(self):
        for w in self._frame_graficos.winfo_children():
            w.destroy()

        gastos  = gs.listar()
        dividas = ds.listar()

        fig, axes = plt.subplots(2, 2, figsize=(11, 7))
        fig.patch.set_facecolor(FUNDO)
        plt.subplots_adjust(hspace=0.45, wspace=0.35)

        self._pizza_categorias(axes[0][0], gastos)
        self._barras_dividas(axes[0][1], dividas)
        self._linha_evolucao(axes[1][0])
        self._top5(axes[1][1], gastos)

        canvas = FigureCanvasTkAgg(fig, master=self._frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _pizza_categorias(self, ax, gastos):
        ax.set_facecolor(CARD_BG)
        if gastos:
            cats = {}
            for g in gastos:
                cats[g.categoria or "Outros"] = \
                    cats.get(g.categoria or "Outros", 0) + (g.valor or 0)
            cores = ["#7c3aed","#a78bfa","#c4b5fd","#6d28d9",
                     "#4c1d95","#ddd6fe","#8b5cf6"]
            ax.pie(cats.values(), labels=cats.keys(),
                   colors=cores[:len(cats)], autopct="%1.1f%%",
                   textprops={"color": TEXTO, "fontsize": 8},
                   wedgeprops={"linewidth": 2, "edgecolor": FUNDO})
        else:
            ax.text(0.5, 0.5, "Sem dados", ha="center",
                    va="center", color=TEXTO_MUTED, fontsize=11)
        ax.set_title("Gastos por categoria", color=VIOLETA,
                     fontsize=11, fontweight="bold")

    def _barras_dividas(self, ax, dividas):
        ax.set_facecolor(CARD_BG)
        if dividas:
            credores  = [d.credor for d in dividas]
            pagos     = [d.valor_pago or 0 for d in dividas]
            pendentes = [d.valor_pendente for d in dividas]
            x = range(len(credores))
            ax.bar(x, pagos,     label="Pago",     color=ROXO_CLARO, width=0.5)
            ax.bar(x, pendentes, label="Pendente", color="#e74c3c",
                   width=0.5, bottom=pagos)
            ax.set_xticks(list(x))
            ax.set_xticklabels(credores, color=TEXTO, fontsize=8, rotation=15)
            ax.tick_params(colors=TEXTO)
            ax.yaxis.set_tick_params(labelcolor=TEXTO)
            ax.legend(facecolor=ROXO_ESCURO, labelcolor=TEXTO, fontsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(ROXO_MEDIO)
        else:
            ax.text(0.5, 0.5, "Sem dados", ha="center",
                    va="center", color=TEXTO_MUTED, fontsize=11)
        ax.set_title("Dívidas: pago vs pendente", color=VIOLETA,
                     fontsize=11, fontweight="bold")

    def _linha_evolucao(self, ax):
        ax.set_facecolor(CARD_BG)
        dados = gs.por_mes()
        if dados:
            labels  = list(dados.keys())
            valores = list(dados.values())
            x       = range(len(labels))
            ax.plot(x, valores, color=VIOLETA, linewidth=2.5, zorder=3)
            ax.scatter(x, valores, color=ROXO_CLARO, s=40, zorder=4)
            ax.fill_between(x, valores, alpha=0.15, color=ROXO_CLARO)
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, color=TEXTO, fontsize=7, rotation=30)
            ax.tick_params(colors=TEXTO)
            ax.yaxis.set_tick_params(labelcolor=TEXTO)
            for spine in ax.spines.values():
                spine.set_edgecolor(ROXO_MEDIO)
        else:
            ax.text(0.5, 0.5, "Sem dados", ha="center",
                    va="center", color=TEXTO_MUTED, fontsize=11)
        ax.set_title("Evolução dos gastos", color=VIOLETA,
                     fontsize=11, fontweight="bold")

    def _top5(self, ax, gastos):
        ax.set_facecolor(CARD_BG)
        if gastos:
            top5    = sorted(gastos, key=lambda g: g.valor or 0, reverse=True)[:5]
            nomes   = [g.descricao[:14] for g in top5]
            valores = [g.valor or 0 for g in top5]
            bars    = ax.barh(nomes, valores, color=ROXO_CLARO, height=0.5)
            ax.bar_label(bars, fmt="R$%.0f", color=TEXTO, fontsize=8, padding=4)
            ax.tick_params(colors=TEXTO)
            ax.xaxis.set_tick_params(labelcolor=TEXTO)
            for spine in ax.spines.values():
                spine.set_edgecolor(ROXO_MEDIO)
            ax.invert_yaxis()
        else:
            ax.text(0.5, 0.5, "Sem dados", ha="center",
                    va="center", color=TEXTO_MUTED, fontsize=11)
        ax.set_title("Top 5 maiores gastos", color=VIOLETA,
                     fontsize=11, fontweight="bold")