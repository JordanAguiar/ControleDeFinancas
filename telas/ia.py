import customtkinter as ctk
from dados import resumo_financeiro
from ia import analisar_financas
from .base import ROXO_MEDIO, ROXO_CLARO, VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED


class IAFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)
        self._montar()

    def _montar(self):
        ctk.CTkLabel(self, text="Assistente Financeiro IA",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 4))

        ctk.CTkLabel(self,
                     text="Faça uma pergunta ou clique em Analisar para uma análise geral",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXTO_MUTED).pack(anchor="w", padx=32, pady=(0, 16))

        frame_input = ctk.CTkFrame(self, fg_color="transparent")
        frame_input.pack(fill="x", padx=32)

        self.entry_pergunta = ctk.CTkEntry(
            frame_input,
            placeholder_text="Ex: Como posso reduzir meus gastos?",
            width=560, height=40, corner_radius=10,
            fg_color=CARD_BG, text_color=TEXTO, border_color=ROXO_CLARO)
        self.entry_pergunta.pack(side="left", padx=(0, 12))

        ctk.CTkButton(frame_input, text="Analisar com IA",
                      command=self._consultar,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=10,
                      width=160, height=40).pack(side="left")

        self.texto_ia = ctk.CTkTextbox(
            self, fg_color=CARD_BG, text_color=TEXTO,
            font=ctk.CTkFont(size=12), corner_radius=16,
            border_width=1, border_color=ROXO_MEDIO, wrap="word")
        self.texto_ia.pack(fill="both", expand=True, padx=32, pady=16)

    def _consultar(self):
        self.texto_ia.delete("1.0", "end")
        self.texto_ia.insert("end", "Consultando IA, aguarde...")
        self.update()
        pergunta = self.entry_pergunta.get().strip() or None
        resposta = analisar_financas(resumo_financeiro(), pergunta)
        self.texto_ia.delete("1.0", "end")
        self.texto_ia.insert("end", resposta)