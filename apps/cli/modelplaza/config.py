import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".modelplaza"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "token"

DEFAULT_API_URL = "http://localhost:8000/api/v1"


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_api_url() -> str:
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        return config.get("api_url", DEFAULT_API_URL)
    return DEFAULT_API_URL


def save_token(token: str):
    ensure_config_dir()
    TOKEN_FILE.write_text(token)


def get_token() -> str | None:
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def clear_token():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
