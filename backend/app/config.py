"""Zentrale Konfiguration aus Umgebungsvariablen.

Die App laeuft out-of-the-box ohne API-Key (LLM_PROVIDER=mock).
Sobald ANTHROPIC_API_KEY gesetzt ist, werden echte KI-Reports erzeugt.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", DATA_DIR / "uploads"))
DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "ausschusslens.db"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6").strip()

# Provider: "auto" (default) waehlt anthropic wenn Key vorhanden, sonst mock.
_provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
if _provider == "auto":
    LLM_PROVIDER = "anthropic" if ANTHROPIC_API_KEY else "mock"
else:
    LLM_PROVIDER = _provider

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# Verzeichnisse sicherstellen
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
