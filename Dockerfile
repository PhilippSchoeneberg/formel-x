FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY src ./src

RUN useradd --create-home formelx
USER formelx

EXPOSE 8000

# Configuration comes from environment variables (see .env.example).
# Migrations run on every start; they are a no-op when the schema is current.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
