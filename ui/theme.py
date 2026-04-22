import customtkinter as ctk

# ── Paleta de cores ──────────────────────────────────────────
ROXO_ESCURO  = "#1e0a3c"
ROXO_MEDIO   = "#3b1f6e"
ROXO_CLARO   = "#7c3aed"
VIOLETA      = "#a78bfa"
FUNDO        = "#12002a"
CARD_BG      = "#1e0a3c"
TEXTO        = "#f3f0ff"
TEXTO_MUTED  = "#a78bfa"

# ── Cores semânticas ─────────────────────────────────────────
VERDE        = "#1d9e75"
VERDE_HOVER  = "#145f47"
LARANJA      = "#e67e22"
LARANJA_HOVER= "#b35c00"
VERMELHO     = "#e74c3c"
VERMELHO_ESC = "#7f1d1d"
VERMELHO_HOV = "#991b1b"


def aplicar_tema():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def fonte(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(size=size, weight=weight)