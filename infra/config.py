import json
import os
from pathlib import Path
from core.exceptions import ConfiguracaoError

CONFIG_DIR  = Path(os.getenv("APPDATA", Path.home())) / "FinanceiroPessoal"
CONFIG_FILE = CONFIG_DIR / "config.json"


def salvar_config(api_key: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)


def carregar_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def api_key_configurada() -> bool:
    return bool(carregar_config().get("api_key", "").strip())


def obter_api_key() -> str:
    return carregar_config().get("api_key", "")