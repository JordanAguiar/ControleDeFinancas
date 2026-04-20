import json
import os
from pathlib import Path

# Salva a config na pasta do usuário (AppData no Windows)
CONFIG_DIR  = Path(os.getenv("APPDATA", Path.home())) / "FinanceiroPessoal"
CONFIG_FILE = CONFIG_DIR / "config.json"


def salvar_config(api_key: str):
    """Salva a chave da API localmente no computador do usuário."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)


def carregar_config() -> dict:
    """Retorna a configuração salva ou um dicionário vazio."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def api_key_configurada() -> bool:
    """Retorna True se a chave já foi salva."""
    config = carregar_config()
    return bool(config.get("api_key", "").strip())


def obter_api_key() -> str:
    """Retorna a chave salva ou string vazia."""
    return carregar_config().get("api_key", "")