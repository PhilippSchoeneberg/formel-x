# Development

## Setup

Requires [uv](https://docs.astral.sh/uv/) (`brew install uv`), Python 3.11 or newer (uv can install it) and Docker (for PostgreSQL).

```bash
uv sync                              # creates .venv with all dependencies from uv.lock
uv run playwright install chromium   # browser for the end-to-end tests
cp .env.example .env
```

In `.env`, set:

- `POSTGRES_PASSWORD` – any password for the local database
- `DATABASE_URL=postgresql+asyncpg://formelx:<POSTGRES_PASSWORD>@localhost:5432/formelx`
- `SESSION_SECRET` – any random string
- `SECURE_COOKIES=false`, otherwise the browser won't send the login cookie over plain `http://`

## Run

Start the database and create the tables (once, and again after pulling new migrations):

```bash
docker compose up -d db
uv run alembic upgrade head
```

Then, from the repository root:

```bash
uv run uvicorn src.backend.main:app --reload
```

Open http://127.0.0.1:8000. The API docs are at http://127.0.0.1:8000/api/docs.

The frontend has no build step: edit files in `src/frontend` and reload the page.

To run the whole stack in Docker (as on the server) use `docker compose up -d --build`. Set
`APP_PORT` or `DB_PORT` in `.env` if port 8000 or 5432 is taken.

## Dependencies

Dependencies are declared in `pyproject.toml` and pinned in `uv.lock` (commit both).

```bash
uv add <package>              # runtime dependency
uv add --dev <package>        # test/dev dependency
uv lock --upgrade             # update everything within the declared ranges
```

## Tests

```bash
uv run pytest                  # everything
uv run pytest -m "not e2e"     # skip the browser tests
```

- `tests/test_api.py` runs the real FastAPI app and database code against SQLite in memory,
  so it needs no running database and no `.env`.
- `tests/e2e/` starts the app on a temporary SQLite database and drives it with Playwright
  (headless Chromium). Add `--headed` to watch the browser. To run them against PostgreSQL, point
`TEST_DATABASE_URL` at an **empty** database that may be wiped:

```bash
docker compose exec db createdb -U formelx formelx_test
TEST_DATABASE_URL=postgresql+asyncpg://formelx:<password>@localhost:5432/formelx_test uv run pytest tests/test_api.py
```

## Changing the schema

1. Change the tables in `src/backend/tables.py`.
2. Generate a migration and review it:
   ```bash
   uv run alembic revision --autogenerate -m "Add something"
   ```
3. Apply it with `uv run alembic upgrade head`. `alembic check` reports whether the tables
   and the migrations still match.

The app container applies migrations itself on every start.

## Translations

Translations are JSON files in `src/frontend/locales/` (`de`, `en`, `es`, `fr`, `nl`).

- Keys are snake_case ids (`"new_category"`), not English text.
- Every value is a complete phrase or sentence. Variable parts are named placeholders:
  `"where_is": "Wo befindet sich {element}?"`, used as `t("where_is", { element })`.
- Don't build sentences from several keys: word order and grammar differ between languages.
- When you add a key, add it to **all five** files. Missing keys fall back to English, then
  to the key itself.
- Tone is informal (du / tú / tu / je). Use the quote marks of each language:
  “…” (en), „…“ (de), «…» (es), « … » (fr), ‘…’ (nl).
- Element names from the database (`hydrogen`, …) are translation keys too.

To add a language, add `<code>.json` and register it in `LANGUAGES` in
`src/frontend/js/i18n.js`.

## Conventions

- Backend: one router per resource in `src/backend/routers`; database access only through
  `Database` in `database.py`; schema in `tables.py` plus an Alembic migration; request
  validation in `schemas.py`; ownership checks via the dependencies in `security.py`.
- Frontend: views in `js/views` render into `<main>` with the `h()` helper from `js/ui.js`.
  All user-visible text goes through `t()`. State changes that affect the whole page
  call `notify()` from `store.js`, which re-renders the header and the current view.
- Commit messages are short imperative English sentences.
