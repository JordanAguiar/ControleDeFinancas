import customtkinter as ctk
from datetime import datetime, timedelta
from ui.theme import (ROXO_ESCURO, ROXO_MEDIO, ROXO_CLARO,
                      VIOLETA, TEXTO, TEXTO_MUTED)


def campo(parent, label: str, row: int) -> ctk.CTkEntry:
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


def campo_data(parent, row: int,
               label: str = "Data",
               atalhos: list = None) -> ctk.CTkEntry:
    """Campo de data com botões de atalho."""
    if atalhos is None:
        atalhos = [("Hoje", 0), ("Ontem", -1), ("Anteontem", -2)]

    parent.columnconfigure(0, weight=0, minsize=180)
    parent.columnconfigure(1, weight=1)

    ctk.CTkLabel(parent, text=label, text_color=TEXTO_MUTED,
                 font=ctk.CTkFont(size=12)
                 ).grid(row=row, column=0, sticky="w", padx=20, pady=6)

    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=6)

    entry = ctk.CTkEntry(frame, placeholder_text="dd/mm/aaaa",
                         height=36, corner_radius=8, width=140,
                         fg_color=ROXO_ESCURO, text_color=TEXTO,
                         border_color=ROXO_CLARO)
    entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
    entry.pack(side="left", padx=(0, 8))

    def set_data(d, e=entry):
        e.delete(0, "end")
        e.insert(0, (datetime.now() + timedelta(days=d)).strftime("%d/%m/%Y"))

    for label_btn, dias in atalhos:
        ctk.CTkButton(
            frame, text=label_btn,
            command=lambda d=dias: set_data(d),
            fg_color="transparent", hover_color=ROXO_MEDIO,
            text_color=VIOLETA, corner_radius=6,
            border_width=1, border_color=ROXO_MEDIO,
            width=80, height=28,
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=(0, 4))

    return entry


def botao_primario(parent, texto: str, comando,
                   cor=ROXO_CLARO, cor_hover=ROXO_MEDIO,
                   **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        fg_color=cor, hover_color=cor_hover,
        text_color=TEXTO, corner_radius=10,
        **kwargs)


def botao_perigo(parent, texto: str, comando, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        fg_color="#7f1d1d", hover_color="#991b1b",
        text_color=TEXTO, corner_radius=10,
        **kwargs)


def botao_outline(parent, texto: str, comando, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        fg_color="transparent", hover_color=ROXO_MEDIO,
        text_color=TEXTO_MUTED, corner_radius=10,
        border_width=1, border_color=ROXO_MEDIO,
        **kwargs)