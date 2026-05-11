import json
import os
from pathlib import Path

CONFIG_DIR  = Path.home() / ".config" / "cybtl"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "api_url":   "https://www.cyber-tools.dev",
    "timeout":   60,
    "save_dir":  str(Path.home() / "cybtl-reports"),
}


def load() -> dict:
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def get(key: str, default=None):
    return load().get(key, default)


def set_key(key: str, value) -> None:
    cfg = load()
    cfg[key] = value
    save(cfg)


def show() -> str:
    cfg = load()
    lines = []
    for k, v in cfg.items():
        lines.append(f"  {k:<14} {v}")
    return "\n".join(lines)