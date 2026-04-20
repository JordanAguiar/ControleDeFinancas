import customtkinter as ctk
from tkinter import messagebox
from config import salvar_config, api_key_configurada

ROXO_ESCURO  = "#1e0a3c"
ROXO_MEDIO   = "#3b1f6e"
ROXO_CLARO   = "#7c3aed"
VIOLETA      = "#a78bfa"
FUNDO        = "#12002a"
CARD_BG      = "#1e0a3c"
TEXTO        = "#f3f0ff"
TEXTO_MUTED  = "#a78bfa"

PASSOS = [
    {
        "titulo": "Bem-vindo ao Financeiro Pessoal!",
        "icone": "💰",
        "descricao": (
            "Este app ajuda você a controlar seus gastos e dívidas "
            "com o auxílio de inteligência artificial.\n\n"
            "Vamos fazer uma configuração rápida antes de começar."
        )
    },
    {
        "titulo": "Registre seus gastos",
        "icone": "📝",
        "descricao": (
            "Na aba Gastos, você pode registrar qualquer gasto do dia a dia "
            "informando a descrição, categoria e valor.\n\n"
            "Todos os dados ficam salvos em uma planilha Excel "
            "na mesma pasta do app."
        )
    },
    {
        "titulo": "Controle suas dívidas",
        "icone": "📋",
        "descricao": (
            "Na aba Dívidas, cadastre suas dívidas com credor, "
            "valor total, quanto já pagou e a data de vencimento.\n\n"
            "O app alerta automaticamente quando uma dívida está "
            "vencida ou prestes a vencer."
        )
    },
    {
        "titulo": "Dashboards e gráficos",
        "icone": "📊",
        "descricao": (
            "Na aba Gráficos você visualiza:\n\n"
            "• Gastos por categoria\n"
            "• Evolução dos gastos ao longo do tempo\n"
            "• Situação das dívidas\n"
            "• Top 5 maiores gastos"
        )
    },
    {
        "titulo": "Assistente de IA",
        "icone": "🤖",
        "descricao": (
            "O assistente analisa sua situação financeira e responde "
            "perguntas como:\n\n"
            "• Como posso economizar?\n"
            "• Qual dívida devo priorizar?\n"
            "• Como está minha saúde financeira?\n\n"
            "Para isso, precisamos da sua chave da API do Groq."
        )
    },
    {
        "titulo": "Configure sua chave de API",
        "icone": "🔑",
        "descricao": (
            "Para usar o assistente de IA, você precisa de uma chave "
            "gratuita do Groq.\n\n"
            "1. Acesse console.groq.com\n"
            "2. Crie uma conta gratuita\n"
            "3. Vá em API Keys → Create API Key\n"
            "4. Cole a chave no campo abaixo\n\n"
            "A chave é salva no seu computador e não é compartilhada."
        ),
        "pede_api": True
    },
]


class TelaOnboarding(ctk.CTkToplevel):
    def __init__(self, parent, ao_finalizar):
        super().__init__(parent)
        self.ao_finalizar = ao_finalizar
        self.passo_atual  = 0

        self.title("Configuração inicial")
        self.geometry("560x480")
        self.configure(fg_color=FUNDO)
        self.resizable(False, False)
        self.grab_set()  # trava foco nesta janela

        self._montar()
        self._atualizar_passo()

    def _montar(self):
        # Ícone e título
        self.label_icone = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=52))
        self.label_icone.pack(pady=(36, 8))

        self.label_titulo = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=VIOLETA)
        self.label_titulo.pack(pady=(0, 12))

        self.label_desc = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=13),
            text_color=TEXTO,
            wraplength=460,
            justify="left")
        self.label_desc.pack(padx=40, pady=(0, 16))

        # Campo de API (aparece só no último passo)
        self.frame_api = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_api = ctk.CTkEntry(
            self.frame_api,
            placeholder_text="Cole sua chave aqui: gsk_...",
            width=400, height=40, corner_radius=10,
            fg_color=CARD_BG, text_color=TEXTO,
            border_color=ROXO_CLARO,
            show="*"
        )
        self.entry_api.pack(pady=4)

        ctk.CTkLabel(
            self.frame_api,
            text="A chave fica salva apenas no seu computador",
            font=ctk.CTkFont(size=11),
            text_color=TEXTO_MUTED
        ).pack()

        # Indicador de progresso (bolinhas)
        self.frame_dots = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_dots.pack(pady=12)

        self.dots = []
        for i in range(len(PASSOS)):
            dot = ctk.CTkLabel(self.frame_dots, text="●",
                               font=ctk.CTkFont(size=10))
            dot.pack(side="left", padx=3)
            self.dots.append(dot)

        # Botões
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=8)

        self.btn_voltar = ctk.CTkButton(
            frame_btns, text="Voltar",
            command=self._voltar,
            fg_color="transparent", hover_color=ROXO_MEDIO,
            text_color=TEXTO_MUTED, corner_radius=10,
            border_width=1, border_color=ROXO_MEDIO,
            width=120, height=40
        )
        self.btn_voltar.pack(side="left", padx=8)

        self.btn_avancar = ctk.CTkButton(
            frame_btns, text="Próximo",
            command=self._avancar,
            fg_color=ROXO_CLARO, hover_color=ROXO_MEDIO,
            text_color=TEXTO, corner_radius=10,
            width=160, height=40
        )
        self.btn_avancar.pack(side="left", padx=8)

    def _atualizar_passo(self):
        passo = PASSOS[self.passo_atual]
        self.label_icone.configure(text=passo["icone"])
        self.label_titulo.configure(text=passo["titulo"])
        self.label_desc.configure(text=passo["descricao"])

        # Mostra ou esconde campo de API
        if passo.get("pede_api"):
            self.frame_api.pack(pady=8)
        else:
            self.frame_api.pack_forget()

        # Atualiza bolinhas
        for i, dot in enumerate(self.dots):
            dot.configure(text_color=VIOLETA if i == self.passo_atual else ROXO_MEDIO)

        # Botão voltar
        self.btn_voltar.configure(
            state="normal" if self.passo_atual > 0 else "disabled"
        )

        # Botão avançar
        ultimo = self.passo_atual == len(PASSOS) - 1
        self.btn_avancar.configure(text="Concluir" if ultimo else "Próximo")

    def _avancar(self):
        passo = PASSOS[self.passo_atual]

        # Valida chave se estiver no passo de API
        if passo.get("pede_api"):
            api_key = self.entry_api.get().strip()
            if not api_key:
                messagebox.showwarning(
                    "Chave necessária",
                    "Por favor, insira sua chave da API do Groq para continuar.\n"
                    "Acesse console.groq.com para obtê-la gratuitamente."
                )
                return
            salvar_config(api_key)

        if self.passo_atual < len(PASSOS) - 1:
            self.passo_atual += 1
            self._atualizar_passo()
        else:
            self.destroy()
            self.ao_finalizar()

    def _voltar(self):
        if self.passo_atual > 0:
            self.passo_atual -= 1
            self._atualizar_passo()