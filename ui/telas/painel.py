import customtkinter as ctk
from tkinter import messagebox
from ui.telas.base import TelaBase
from ui.components import Card, botao_primario
from ui.theme import (FUNDO, CARD_BG, ROXO_MEDIO, ROXO_CLARO,
                      VIOLETA, TEXTO, TEXTO_MUTED, VERDE)
from core.services import resumo as resumo_svc
from core.services import dividas as dividas_svc
import infra


class PainelTela(TelaBase):

    def _montar(self):
        ctk.CTkLabel(self, text="Painel Financeiro",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=VIOLETA).pack(anchor="w", padx=32, pady=(28, 4))

        ctk.CTkLabel(self, text="Visão geral do mês atual",
                     font=ctk.CTkFont(size=13),
                     text_color=TEXTO_MUTED).pack(anchor="w", padx=32, pady=(0, 12))

        # Banner de alertas
        self.frame_alertas = ctk.CTkFrame(
            self, fg_color="#3b0a0a", corner_radius=12,
            border_width=1, border_color="#e74c3c")
        self.label_alertas = ctk.CTkLabel(
            self.frame_alertas, text="",
            font=ctk.CTkFont(size=12), text_color="#fca5a5",
            justify="left", wraplength=700)
        self.label_alertas.pack(padx=20, pady=12)

        # Cards
        frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        frame_cards.pack(fill="x", padx=32, pady=(0, 8))

        dados_cards = [
            ("Gastos do mês",    "total_gastos",     "#e74c3c", "📉"),
            ("Receitas do mês",  "total_receitas",   VERDE,     "📈"),
            ("Saldo do mês",     "saldo",            ROXO_CLARO,"💰"),
            ("Dívidas Pendentes","dividas_pendentes","#e67e22",  "⚠️"),
        ]

        self._cards = {}
        for i, (titulo, chave, cor, icone) in enumerate(dados_cards):
            frame_cards.columnconfigure(i, weight=1)
            card = Card(frame_cards, titulo=titulo, icone=icone, cor_valor=cor)
            card.grid(row=0, column=i, padx=10, pady=8, sticky="nsew")
            self._cards[chave] = card

        botao_primario(self, "Atualizar", self.atualizar,
                       width=140, height=38).pack(anchor="w", padx=32, pady=12)

        # Meta mensal
        self._montar_meta()

    def _montar_meta(self):
        frame_meta = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16,
                                  border_width=1, border_color=ROXO_MEDIO)
        frame_meta.pack(fill="x", padx=32, pady=(0, 8))
        frame_meta.columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_meta, text="Meta de economia mensal",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VIOLETA
                     ).grid(row=0, column=0, columnspan=2,
                            padx=20, pady=(16, 4), sticky="w")

        self.entry_meta = ctk.CTkEntry(
            frame_meta, placeholder_text="Ex: 1500.00",
            height=36, corner_radius=8,
            fg_color="#12002a", text_color=TEXTO,
            border_color=ROXO_CLARO)
        self.entry_meta.grid(row=1, column=0, sticky="ew",
                             padx=(20, 8), pady=(0, 8))

        botao_primario(frame_meta, "Salvar Meta", self._salvar_meta,
                       width=130, height=36
                       ).grid(row=1, column=1, sticky="w",
                               padx=(0, 20), pady=(0, 8))

        self.label_meta = ctk.CTkLabel(
            frame_meta, text="Meta não definida",
            font=ctk.CTkFont(size=11), text_color=TEXTO_MUTED)
        self.label_meta.grid(row=2, column=0, columnspan=2,
                             padx=20, sticky="w")

        self.barra_meta = ctk.CTkProgressBar(
            frame_meta, height=14, corner_radius=8,
            fg_color=ROXO_MEDIO, progress_color=ROXO_CLARO)
        self.barra_meta.set(0)
        self.barra_meta.grid(row=3, column=0, columnspan=2,
                             padx=20, pady=(4, 16), sticky="ew")

    def atualizar(self):
        r = resumo_svc.calcular()
        self._cards["total_gastos"].atualizar(    f"R$ {r.total_gastos:.2f}")
        self._cards["total_receitas"].atualizar(  f"R$ {r.total_receitas:.2f}")
        self._cards["saldo"].atualizar(           f"R$ {r.saldo:.2f}")
        self._cards["dividas_pendentes"].atualizar(f"R$ {r.dividas_pendentes:.2f}")
        self._atualizar_meta()

    def verificar_alertas(self):
        vencidas, vencendo = dividas_svc.verificar_alertas()
        if not vencidas and not vencendo:
            self.frame_alertas.pack_forget()
            return

        linhas = []
        if vencidas:
            linhas.append("DÍVIDAS VENCIDAS:")
            for d in vencidas:
                linhas.append(
                    f"  • {d['credor']} — {d['descricao']} "
                    f"(R$ {d['valor_total']:.2f}) — "
                    f"{d['dias_atraso']} dia(s) em atraso")
        if vencendo:
            if linhas:
                linhas.append("")
            linhas.append("VENCENDO EM BREVE:")
            for d in vencendo:
                linhas.append(
                    f"  • {d['credor']} — {d['descricao']} "
                    f"(R$ {d['valor_total']:.2f}) — "
                    f"vence em {d['dias_restantes']} dia(s)")

        self.label_alertas.configure(text="\n".join(linhas))
        self.frame_alertas.pack(fill="x", padx=32, pady=(0, 12))

        partes = []
        if vencidas:
            partes.append(f"{len(vencidas)} dívida(s) vencida(s)")
        if vencendo:
            partes.append(f"{len(vencendo)} vencendo em até 7 dias")

        messagebox.showwarning(
            "Alerta de Dívidas",
            f"Atenção! Você tem {' e '.join(partes)}.\n\nVerifique o Painel.")

    def _salvar_meta(self):
        valor = self.entry_meta.get().strip()
        if not valor:
            messagebox.showwarning("Atenção", "Informe um valor para a meta.")
            return
        try:
            resumo_svc.salvar_meta(float(valor.replace(",", ".")))
            self.entry_meta.delete(0, "end")
            self._atualizar_meta()
            messagebox.showinfo("Sucesso", "Meta salva!")
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Ex: 1500.00")

    def _atualizar_meta(self):
        meta = resumo_svc.buscar_meta()
        if meta <= 0:
            self.label_meta.configure(text="Meta não definida")
            self.barra_meta.set(0)
            return
        gasto     = resumo_svc.calcular().total_gastos
        progresso = min(gasto / meta, 1.0)
        cor = "#1d9e75" if progresso < 0.6 else "#e67e22" if progresso < 0.85 else "#e74c3c"
        self.barra_meta.configure(progress_color=cor)
        self.barra_meta.set(progresso)
        self.label_meta.configure(
            text=f"Gasto: R$ {gasto:.2f}  |  Meta: R$ {meta:.2f}  |  {progresso*100:.1f}% utilizado")