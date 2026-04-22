import customtkinter as ctk
from datetime import datetime


class CampoData(ctk.CTkFrame):
    """Campo de data com botões de atalho e validação."""

    def __init__(self, parent, fg_color, roxo_escuro, roxo_claro,
                 roxo_medio, violeta, texto, texto_muted, **kwargs):
        super().__init__(parent, fg_color=fg_color, **kwargs)

        self.roxo_claro = roxo_claro
        self.roxo_medio = roxo_medio
        self.violeta    = violeta

        self.columnconfigure(0, weight=0, minsize=180)
        self.columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Data", text_color=texto_muted,
                     font=ctk.CTkFont(size=12)
                     ).grid(row=0, column=0, sticky="w", padx=20, pady=(6, 0))

        frame_entry = ctk.CTkFrame(self, fg_color="transparent")
        frame_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(6, 0))
        frame_entry.columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            frame_entry,
            placeholder_text="dd/mm/aaaa",
            height=36, corner_radius=8,
            fg_color=roxo_escuro, text_color=texto,
            border_color=roxo_claro)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Atalhos
        frame_atalhos = ctk.CTkFrame(self, fg_color="transparent")
        frame_atalhos.grid(row=1, column=1, sticky="w",
                           padx=(0, 20), pady=(4, 6))

        for label, dias in [("Hoje", 0), ("Ontem", -1), ("Anteontem", -2)]:
            ctk.CTkButton(
                frame_atalhos, text=label,
                command=lambda d=dias: self._set_data(d),
                fg_color="transparent",
                hover_color=roxo_medio,
                text_color=violeta,
                corner_radius=6,
                border_width=1,
                border_color=roxo_medio,
                width=80, height=24,
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=(0, 6))

    def _set_data(self, delta_dias):
        from datetime import timedelta
        dt = datetime.now() + __import__("datetime").timedelta(days=delta_dias)
        self.entry.delete(0, "end")
        self.entry.insert(0, dt.strftime("%d/%m/%Y"))

    def get(self):
        valor = self.entry.get().strip()
        try:
            datetime.strptime(valor, "%d/%m/%Y")
            return valor
        except ValueError:
            return datetime.now().strftime("%d/%m/%Y")

    def delete(self, *args):
        self.entry.delete(0, "end")
        self.entry.insert(0, datetime.now().strftime("%d/%m/%Y"))