import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import CARD_BG, ROXO_CLARO, ROXO_MEDIO, VIOLETA, TEXTO, TEXTO_MUTED


def limpar(frame: ctk.CTkFrame):
    """Remove todos os widgets de um frame."""
    for w in frame.winfo_children():
        w.destroy()


def linha(frame: ctk.CTkFrame, dados: dict,
          figsize: tuple = (10, 2.2)):
    """Gráfico de linha com área preenchida e anotações."""
    limpar(frame)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)

    if dados:
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
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def barras(frame: ctk.CTkFrame, dados: dict,
           cor: str = ROXO_CLARO, figsize: tuple = (10, 2.2)):
    """Gráfico de barras simples."""
    limpar(frame)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)

    if dados:
        labels  = list(dados.keys())
        valores = list(dados.values())
        ax.bar(labels, valores, color=cor, width=0.5)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, color=TEXTO, fontsize=7, rotation=30)
        ax.yaxis.set_tick_params(labelcolor=TEXTO)
        ax.tick_params(colors=TEXTO)
        for spine in ax.spines.values():
            spine.set_edgecolor(ROXO_MEDIO)
    else:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                color=TEXTO_MUTED, fontsize=11)

    plt.tight_layout(pad=1.0)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def pizza(frame: ctk.CTkFrame, dados: dict,
          figsize: tuple = (5, 3)):
    """Gráfico de pizza por categoria."""
    limpar(frame)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)

    if dados:
        cores = ["#7c3aed","#a78bfa","#c4b5fd","#6d28d9",
                 "#4c1d95","#ddd6fe","#8b5cf6","#1d9e75"]
        ax.pie(dados.values(), labels=dados.keys(),
               colors=cores[:len(dados)], autopct="%1.1f%%",
               textprops={"color": TEXTO, "fontsize": 8},
               wedgeprops={"linewidth": 2, "edgecolor": CARD_BG})
    else:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                color=TEXTO_MUTED, fontsize=11)

    plt.tight_layout(pad=1.0)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def barras_empilhadas(frame: ctk.CTkFrame,
                      categorias: list,
                      serie_a: list, label_a: str,
                      serie_b: list, label_b: str,
                      cor_a: str = ROXO_CLARO,
                      cor_b: str = "#e74c3c",
                      figsize: tuple = (10, 2.5)):
    """Gráfico de barras empilhadas (ex: pago vs pendente)."""
    limpar(frame)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)

    if categorias:
        x = range(len(categorias))
        ax.bar(x, serie_a, label=label_a, color=cor_a, width=0.5)
        ax.bar(x, serie_b, label=label_b, color=cor_b,
               width=0.5, bottom=serie_a)
        ax.set_xticks(list(x))
        ax.set_xticklabels(categorias, color=TEXTO, fontsize=8, rotation=15)
        ax.tick_params(colors=TEXTO)
        ax.yaxis.set_tick_params(labelcolor=TEXTO)
        ax.legend(facecolor="#1e0a3c", labelcolor=TEXTO, fontsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(ROXO_MEDIO)
    else:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                color=TEXTO_MUTED, fontsize=11)

    plt.tight_layout(pad=1.0)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)