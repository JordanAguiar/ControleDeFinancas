import customtkinter as ctk
import tkinter.ttk as ttk

ROXO_ESCURO  = "#1e0a3c"
ROXO_MEDIO   = "#3b1f6e"
ROXO_CLARO   = "#7c3aed"
VIOLETA      = "#a78bfa"
FUNDO        = "#12002a"
CARD_BG      = "#1e0a3c"
TEXTO        = "#f3f0ff"
TEXTO_MUTED  = "#a78bfa"


def campo(parent, label, row):
    """Campo de formulário responsivo."""
    parent.columnconfigure(0, weight=0, minsize=180)
    parent.columnconfigure(1, weight=1)

    ctk.CTkLabel(parent, text=label, text_color=TEXTO_MUTED,
                 font=ctk.CTkFont(size=12)
                 ).grid(row=row, column=0, sticky="w", padx=20, pady=6)

    entry = ctk.CTkEntry(parent, height=36, corner_radius=8,
                         fg_color=ROXO_ESCURO, text_color=TEXTO,
                         border_color=ROXO_CLARO)
    entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=6)
    return entry


def criar_tabela(parent, colunas, larguras):
    """Tabela responsiva que estica com a janela."""
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
    frame.pack(fill="both", expand=True, padx=32, pady=(0, 20))
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    scroll = ttk.Scrollbar(frame)
    scroll.pack(side="right", fill="y")

    tabela = ttk.Treeview(frame, columns=colunas, show="headings",
                          yscrollcommand=scroll.set,
                          style="Custom.Treeview")

    # Larguras proporcionais — última coluna estica
    for i, (col, larg) in enumerate(zip(colunas, larguras)):
        tabela.heading(col, text=col)
        stretch = True if i == len(colunas) - 1 else False
        tabela.column(col, width=larg, minwidth=60,
                      anchor="center", stretch=stretch)

    tabela.pack(fill="both", expand=True, padx=4, pady=4)
    scroll.config(command=tabela.yview)
    return tabela