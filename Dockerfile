FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install the locked dependencies first so this layer is cached between code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic.ini .
COPY src ./src

RUN useradd --create-home formelx
USER formelx

EXPOSE 8000

# Configuration comes from environment variables (see .env.example).
# Migrations run on every start; they are a no-op when the schema is current.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
