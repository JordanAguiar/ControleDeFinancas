import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from dados import inicializar_arquivo
from config import api_key_configurada
from onboarding import TelaOnboarding
from telas import PainelFrame, GastosFrame, ReceitasFrame, DividasFrame, GraficosFrame, IAFrame

inicializar_arquivo()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ROXO_ESCURO = "#1e0a3c"
ROXO_MEDIO  = "#3b1f6e"
ROXO_CLARO  = "#7c3aed"
VIOLETA     = "#a78bfa"
FUNDO       = "#12002a"
TEXTO       = "#f3f0ff"
TEXTO_MUTED = "#a78bfa"


class AppFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Financeiro Pessoal")
        self.geometry("1100x680")
        self.configure(fg_color=FUNDO)
        self.resizable(True, True)
        self.bind("<F5>", lambda e: self._atualizar_tudo())

        self._criar_sidebar()
        self._criar_telas()
        self._mostrar_aba("painel")

        if not api_key_configurada():
            self.after(200, self._abrir_onboarding)
        else:
            self.after(500, self.telas["painel"].verificar_alertas)

    def _criar_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=ROXO_ESCURO, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="💰 Financeiro",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=VIOLETA).pack(pady=(32, 24), padx=20)

        self.botoes_nav = {}
        itens = [
            ("painel",   "  Painel"),
            ("gastos",   "  Gastos"),
            ("receitas", "  Receitas"),
            ("dividas",  "  Dívidas"),
            ("graficos", "  Gráficos"),
            ("ia",       "  Assistente IA"),
        ]
        for chave, texto in itens:
            btn = ctk.CTkButton(
                sidebar, text=texto,
                command=lambda c=chave: self._mostrar_aba(c),
                fg_color="transparent", hover_color=ROXO_MEDIO,
                text_color=TEXTO, anchor="w",
                font=ctk.CTkFont(size=13), height=44, corner_radius=10)
            btn.pack(fill="x", padx=12, pady=3)
            self.botoes_nav[chave] = btn

        ctk.CTkFrame(sidebar, fg_color=ROXO_MEDIO, height=1).pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(sidebar, text="  Atualizar (F5)",
                      command=self._atualizar_tudo,
                      fg_color="transparent", hover_color=ROXO_MEDIO,
                      text_color=TEXTO_MUTED, anchor="w",
                      font=ctk.CTkFont(size=12), height=36, corner_radius=10
                      ).pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(sidebar, text="v1.0.0",
                     font=ctk.CTkFont(size=11),
                     text_color=TEXTO_MUTED).pack(side="bottom", pady=16)

    def _criar_telas(self):
        container = ctk.CTkFrame(self, fg_color=FUNDO, corner_radius=0)
        container.pack(side="left", fill="both", expand=True)

        self.telas = {
            "painel":   PainelFrame(container),
            "gastos":   GastosFrame(container),
            "receitas": ReceitasFrame(container),
            "dividas":  DividasFrame(container),
            "graficos": GraficosFrame(container),
            "ia":       IAFrame(container),
        }
        for tela in self.telas.values():
            tela.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _mostrar_aba(self, chave):
        self.telas[chave].lift()
        for k, btn in self.botoes_nav.items():
            btn.configure(fg_color=ROXO_CLARO if k == chave else "transparent")
        if chave == "graficos":
            self.telas["graficos"].atualizar()

    def _atualizar_tudo(self):
        self.telas["painel"].atualizar()
        self.telas["gastos"].atualizar()
        self.telas["receitas"].atualizar()
        self.telas["dividas"].atualizar()
        self.telas["graficos"].atualizar()

    def _abrir_onboarding(self):
        TelaOnboarding(self, ao_finalizar=lambda: self.after(300, self.telas["painel"].verificar_alertas))


if __name__ == "__main__":
    app = AppFinanceiro()
    app.mainloop()