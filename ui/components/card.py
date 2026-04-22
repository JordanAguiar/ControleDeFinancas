import customtkinter as ctk
from ui.theme import CARD_BG, ROXO_MEDIO, TEXTO, TEXTO_MUTED, VIOLETA


class Card(ctk.CTkFrame):
    """Card genérico com ícone, título e valor."""

    def __init__(self, parent, titulo: str, icone: str = "",
                 cor_valor: str = TEXTO, **kwargs):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=16,
                         border_width=1, border_color=ROXO_MEDIO, **kwargs)

        if icone:
            ctk.CTkLabel(self, text=icone,
                         font=ctk.CTkFont(size=28)).pack(pady=(18, 4))

        ctk.CTkLabel(self, text=titulo,
                     font=ctk.CTkFont(size=11),
                     text_color=TEXTO_MUTED).pack(fill="x", padx=8)

        self._label_valor = ctk.CTkLabel(
            self, text="—",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=cor_valor)
        self._label_valor.pack(pady=(4, 18), fill="x", padx=8)

    def atualizar(self, valor: str):
        self._label_valor.configure(text=valor)