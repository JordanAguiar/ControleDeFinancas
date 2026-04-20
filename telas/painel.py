import customtkinter as ctk
from tkinter import messagebox
from dados import resumo_financeiro, salvar_meta, carregar_meta, verificar_dividas_vencendo
from .base import ROXO_ESCURO, ROXO_MEDIO, ROXO_CLARO, VIOLETA, FUNDO, CARD_BG, TEXTO, TEXTO_MUTED


class PainelFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=FUNDO, corner_radius=0)

        self._montar()
        self.atualizar()

    def _montar(self):
        ctk.CTkLabel(self, text="Painel Financeiro",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 4))

        ctk.CTkLabel(self, text="Visão geral das suas finanças",
                     font=ctk.CTkFont(size=13),
                     text_color=TEXTO_MUTED).pack(anchor="w", padx=32, pady=(0, 12))

        # Banner de alertas
        self.frame_alertas = ctk.CTkFrame(self, fg_color="#3b0a0a",
                                          corner_radius=12, border_width=1,
                                          border_color="#e74c3c")
        self.label_alertas = ctk.CTkLabel(self.frame_alertas, text="",
                                          font=ctk.CTkFont(size=12),
                                          text_color="#fca5a5",
                                          justify="left", wraplength=700)
        self.label_alertas.pack(padx=20, pady=12)

        # Cards
        frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        frame_cards.pack(fill="x", padx=32)

        dados_cards = [
            ("Total de Gastos",   "total_gastos",     "#e74c3c", "📉"),
            ("Total de Receitas", "total_receitas",   "#1d9e75", "📈"),
            ("Saldo do Período",  "saldo",            "#7c3aed", "💰"),
            ("Dívidas Pendentes", "dividas_pendentes","#e67e22", "⚠️"),
        ]

        self.labels_cards = {}
        for i, (titulo, chave, cor, icone) in enumerate(dados_cards):
            card = ctk.CTkFrame(frame_cards, fg_color=CARD_BG,
                                corner_radius=16, border_width=1,
                                border_color=ROXO_MEDIO)
            card.grid(row=0, column=i, padx=10, pady=8, sticky="nsew")
            frame_cards.columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=icone, font=ctk.CTkFont(size=28)).pack(pady=(18, 4))
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                         text_color=TEXTO_MUTED).pack()
            lbl = ctk.CTkLabel(card, text="R$ 0,00",
                               font=ctk.CTkFont(size=20, weight="bold"),
                               text_color=TEXTO)
            lbl.pack(pady=(4, 18))
            self.labels_cards[chave] = lbl

        ctk.CTkButton(self, text="Atualizar",
                      command=self.atualizar,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=10,
                      width=140, height=38).pack(anchor="w", padx=32, pady=12)

        # Meta mensal
        frame_meta = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16,
                                  border_width=1, border_color=ROXO_MEDIO)
        frame_meta.pack(fill="x", padx=32, pady=(0, 8))

        ctk.CTkLabel(frame_meta, text="Meta de economia mensal",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VIOLETA).grid(row=0, column=0, padx=20, pady=(16, 4), sticky="w")

        frame_meta_input = ctk.CTkFrame(frame_meta, fg_color="transparent")
        frame_meta_input.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")

        self.entry_meta = ctk.CTkEntry(frame_meta_input,
                                       placeholder_text="Ex: 1500.00",
                                       width=200, height=36, corner_radius=8,
                                       fg_color=ROXO_ESCURO, text_color=TEXTO,
                                       border_color=ROXO_CLARO)
        self.entry_meta.pack(side="left", padx=(0, 12))

        ctk.CTkButton(frame_meta_input, text="Salvar Meta",
                      command=self._salvar_meta,
                      fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
                      text_color=TEXTO, corner_radius=8,
                      width=120, height=36).pack(side="left")

        self.label_meta_status = ctk.CTkLabel(frame_meta, text="Meta não definida",
                                              font=ctk.CTkFont(size=11),
                                              text_color=TEXTO_MUTED)
        self.label_meta_status.grid(row=2, column=0, padx=20, sticky="w")

        self.barra_meta = ctk.CTkProgressBar(frame_meta, width=500, height=14,
                                             corner_radius=8, fg_color=ROXO_MEDIO,
                                             progress_color=ROXO_CLARO)
        self.barra_meta.set(0)
        self.barra_meta.grid(row=3, column=0, padx=20, pady=(4, 16), sticky="w")

    def atualizar(self):
        r = resumo_financeiro()
        self.labels_cards["total_gastos"].configure(     text=f"R$ {r['total_gastos']:.2f}")
        self.labels_cards["total_receitas"].configure(   text=f"R$ {r['total_receitas']:.2f}")
        self.labels_cards["saldo"].configure(            text=f"R$ {r['saldo']:.2f}")
        self.labels_cards["dividas_pendentes"].configure(text=f"R$ {r['dividas_pendentes']:.2f}")
        self._atualizar_meta()

    def verificar_alertas(self):
        vencidas, vencendo = verificar_dividas_vencendo()
        if not vencidas and not vencendo:
            self.frame_alertas.pack_forget()
            return

        linhas = []
        if vencidas:
            linhas.append("DÍVIDAS VENCIDAS:")
            for d in vencidas:
                linhas.append(f"  • {d['credor']} — {d['descricao']} (R$ {d['valor_total']:.2f}) — {d['dias_atraso']} dia(s) em atraso")
        if vencendo:
            if linhas: linhas.append("")
            linhas.append("VENCENDO EM BREVE:")
            for d in vencendo:
                linhas.append(f"  • {d['credor']} — {d['descricao']} (R$ {d['valor_total']:.2f}) — vence em {d['dias_restantes']} dia(s)")

        self.label_alertas.configure(text="\n".join(linhas))
        self.frame_alertas.pack(fill="x", padx=32, pady=(0, 12))

        partes = []
        if vencidas: partes.append(f"{len(vencidas)} dívida(s) vencida(s)")
        if vencendo: partes.append(f"{len(vencendo)} vencendo em até 7 dias")
        messagebox.showwarning("Alerta de Dívidas",
                               f"Atenção! Você tem {' e '.join(partes)}.\n\nVerifique o Painel.")

    def _salvar_meta(self):
        valor = self.entry_meta.get().strip()
        if not valor:
            messagebox.showwarning("Atenção", "Informe um valor para a meta.")
            return
        try:
            salvar_meta(float(valor.replace(",", ".")))
            self.entry_meta.delete(0, "end")
            self._atualizar_meta()
            messagebox.showinfo("Sucesso", "Meta salva!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Ex: 1500.00")

    def _atualizar_meta(self):
        meta = carregar_meta()
        if meta <= 0:
            self.label_meta_status.configure(text="Meta não definida")
            self.barra_meta.set(0)
            return
        gasto     = resumo_financeiro()["total_gastos"]
        progresso = min(gasto / meta, 1.0)
        cor = "#1d9e75" if progresso < 0.6 else "#e67e22" if progresso < 0.85 else "#e74c3c"
        self.barra_meta.configure(progress_color=cor)
        self.barra_meta.set(progresso)
        self.label_meta_status.configure(
            text=f"Gasto: R$ {gasto:.2f}  |  Meta: R$ {meta:.2f}  |  {progresso*100:.1f}% utilizado")