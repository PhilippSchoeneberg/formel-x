import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "src" / "frontend"

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str
    session_secret: str
    secure_cookies: bool = True


def _require(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set. Copy .env.example to .env and fill it in.")
    return value


def load_settings():
    return Settings(
        supabase_url=_require("SUPABASE_URL").rstrip("/"),
        supabase_key=_require("SUPABASE_KEY"),
        session_secret=_require("SESSION_SECRET"),
        secure_cookies=os.environ.get("SECURE_COOKIES", "true").strip().lower() not in ("0", "false", "no"),
    )
