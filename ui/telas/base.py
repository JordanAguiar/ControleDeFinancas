import customtkinter as ctk
from ui.theme import FUNDO


class TelaBase(ctk.CTkFrame):
    """Classe base para todas as telas."""

    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        raise NotImplementedError

    def atualizar(self):
        pass