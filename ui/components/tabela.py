import customtkinter as ctk
import tkinter.ttk as ttk
from ui.theme import CARD_BG, ROXO_MEDIO, ROXO_CLARO, VIOLETA, TEXTO


def criar_tabela(parent, colunas: list[str],
                 larguras: list[int]) -> ttk.Treeview:
    """Tabela responsiva com scroll e tema escuro."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=CARD_BG, foreground=TEXTO,
                    fieldbackground=CARD_BG, rowheight=32,
                    font=("Helvetica", 10))
    style.configure("Custom.Treeview.Heading",
                    background=ROXO_MEDIO, foreground=VIOLETA,
                    font=("Helvetica", 10, "bold"), relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", ROXO_CLARO)],
              foreground=[("selected", TEXTO)])

    frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16)
    frame.pack(fill="both", expand=True, padx=32, pady=(0, 12))

    scroll = ttk.Scrollbar(frame)
    scroll.pack(side="right", fill="y")

    tabela = ttk.Treeview(frame, columns=colunas, show="headings",
                          yscrollcommand=scroll.set,
                          style="Custom.Treeview")

    for i, (col, larg) in enumerate(zip(colunas, larguras)):
        tabela.heading(col, text=col)
        stretch = i == len(colunas) - 1
        tabela.column(col, width=larg, minwidth=60,
                      anchor="center", stretch=stretch)

    tabela.pack(fill="both", expand=True, padx=4, pady=4)
    scroll.config(command=tabela.yview)
    return tabela