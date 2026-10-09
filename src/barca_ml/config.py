"""Load config.yaml dan sediakan path absolut relatif ke root repo."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path = ROOT / "configs" / "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def data_path(*parts: str, kind: str = "raw") -> Path:
    cfg = load_config()
    return ROOT / cfg["paths"][kind] / Path(*parts)
