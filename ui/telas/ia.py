import customtkinter as ctk
from tkinter import messagebox
from ui.telas.base import TelaBase
from ui.components import botao_primario
from ui.theme import (FUNDO, CARD_BG, ROXO_MEDIO, ROXO_CLARO,
                      VIOLETA, TEXTO, TEXTO_MUTED)
from core.services import resumo as resumo_svc
from core.exceptions import APIError
import infra


class IATela(TelaBase):

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

        self._entry = ctk.CTkEntry(
            frame_input,
            placeholder_text="Ex: Como posso reduzir meus gastos?",
            height=40, corner_radius=10,
            fg_color=CARD_BG, text_color=TEXTO,
            border_color=ROXO_CLARO)
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        botao_primario(frame_input, "Analisar com IA", self._consultar,
                       width=160, height=40).pack(side="left")

        self._texto = ctk.CTkTextbox(
            self, fg_color=CARD_BG, text_color=TEXTO,
            font=ctk.CTkFont(size=12), corner_radius=16,
            border_width=1, border_color=ROXO_MEDIO, wrap="word")
        self._texto.pack(fill="both", expand=True, padx=32, pady=16)

    def _consultar(self):
        self._texto.delete("1.0", "end")
        self._texto.insert("end", "Consultando IA, aguarde...")
        self.update()

        try:
            resumo   = resumo_svc.calcular().__dict__
            pergunta = self._entry.get().strip() or None
            resposta = infra.analisar(resumo, pergunta)
            self._texto.delete("1.0", "end")
            self._texto.insert("end", resposta)
        except APIError as e:
            self._texto.delete("1.0", "end")
            self._texto.insert("end", f"Erro: {e}")