import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")

from ui.theme import (aplicar_tema, FUNDO, ROXO_ESCURO, ROXO_MEDIO,
                      ROXO_CLARO, VIOLETA, TEXTO, TEXTO_MUTED)
from ui.telas import (PainelTela, GastosTela, ReceitasTela, DividasTela,
                      InvestimentosTela, GraficosTela, IATela)
from infra.config import api_key_configurada
import infra


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        aplicar_tema()
        self.title("Financeiro Pessoal")
        self.geometry("1100x680")
        self.configure(fg_color=FUNDO)
        self.resizable(True, True)
        self.bind("<F5>", lambda e: self._atualizar_tudo())

        infra.inicializar()
        self._criar_sidebar()
        self._criar_telas()
        self._mostrar_aba("painel")

        if not api_key_configurada():
            self.after(200, self._abrir_onboarding)
        else:
            self.after(500, self.telas["painel"].verificar_alertas)

    def _criar_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=ROXO_ESCURO,
                               width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="💰 Financeiro",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=VIOLETA).pack(pady=(32, 24), padx=20)

        self._botoes = {}
        itens = [
            ("painel",        "  Painel"),
            ("gastos",        "  Gastos"),
            ("receitas",      "  Receitas"),
            ("investimentos", "  Investimentos"),
            ("dividas",       "  Dívidas"),
            ("graficos",      "  Gráficos"),
            ("ia",            "  Assistente IA"),
        ]
        for chave, texto in itens:
            btn = ctk.CTkButton(
                sidebar, text=texto,
                command=lambda c=chave: self._mostrar_aba(c),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=TEXTO, anchor="w",
                font=ctk.CTkFont(size=13), height=44, corner_radius=10)
            btn.pack(fill="x", padx=12, pady=3)
            self._botoes[chave] = btn

        ctk.CTkFrame(sidebar, fg_color=ROXO_MEDIO,
                     height=1).pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(sidebar, text="  Atualizar (F5)",
                      command=self._atualizar_tudo,
                      fg_color="transparent", hover_color=ROXO_MEDIO,
                      text_color=TEXTO_MUTED, anchor="w",
                      font=ctk.CTkFont(size=12), height=36,
                      corner_radius=10).pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(sidebar, text="v2.0.0",
                     font=ctk.CTkFont(size=11),
                     text_color=TEXTO_MUTED).pack(side="bottom", pady=16)

    def _criar_telas(self):
        container = ctk.CTkFrame(self, fg_color=FUNDO, corner_radius=0)
        container.pack(side="left", fill="both", expand=True)

        self.telas = {
            "painel":        PainelTela(container),
            "gastos":        GastosTela(container),
            "receitas":      ReceitasTela(container),
            "investimentos": InvestimentosTela(container),
            "dividas":       DividasTela(container),
            "graficos":      GraficosTela(container),
            "ia":            IATela(container),
        }
        for tela in self.telas.values():
            tela.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _mostrar_aba(self, chave: str):
        self.telas[chave].lift()
        for k, btn in self._botoes.items():
            btn.configure(fg_color=ROXO_CLARO if k == chave else "transparent")
        if chave == "graficos":
            self.telas["graficos"].atualizar()

    def _atualizar_tudo(self):
        for tela in self.telas.values():
            tela.atualizar()

    def _abrir_onboarding(self):
        from onboarding import TelaOnboarding
        TelaOnboarding(self, ao_finalizar=lambda: self.after(
            300, self.telas["painel"].verificar_alertas))