import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "src" / "frontend"

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str
    session_secret: str
    secure_cookies: bool = True


def _require(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set. Copy .env.example to .env and fill it in.")
    return value


def normalize_database_url(url):
    """Accepts plain postgres:// URLs and selects the async asyncpg driver for them."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url


def database_url():
    return normalize_database_url(_require("DATABASE_URL"))


def load_settings():
    return Settings(
        database_url=database_url(),
        session_secret=_require("SESSION_SECRET"),
        secure_cookies=os.environ.get("SECURE_COOKIES", "true").strip().lower() not in ("0", "false", "no"),
    )
