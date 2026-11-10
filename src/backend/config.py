"""Configuration from environment variables, with `.env` in the repository root as fallback."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "src" / "frontend"


def normalize_database_url(url):
    """Accepts plain postgres:// URLs and selects the async asyncpg driver for them."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url


class _Base(BaseSettings):
    # Real environment variables win over .env; unrelated .env entries are ignored.
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


class DatabaseSettings(_Base):
    """What Alembic and the import script need."""

    database_url: str

    @field_validator("database_url")
    @classmethod
    def _normalize(cls, value):
        return normalize_database_url(value.strip())


class Settings(DatabaseSettings):
    """Everything the web app needs."""

    # Signs the login cookie: anyone who knows it can log in as any account. Generate it with
    # python -c "import secrets; print(secrets.token_urlsafe(32))"
    session_secret: str = Field(min_length=32)
    secure_cookies: bool = True
    # Comma-separated host names the app answers to, e.g. "formel-x.duckdns.org,localhost".
    # "*" (the default, for development) accepts any Host header.
    allowed_hosts: str = "*"

    @property
    def allowed_host_list(self):
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()] or ["*"]


class SupabaseSettings(_Base):
    """Only for the one-time import from the old Supabase project."""

    supabase_url: str
    supabase_key: str


def database_url():
    return DatabaseSettings().database_url


def load_settings():
    return Settings()
