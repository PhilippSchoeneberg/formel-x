# Development

## Setup

Requires Python 3.11 or newer and Docker (for PostgreSQL).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
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
.venv/bin/alembic upgrade head
```

Then, from the repository root:

```bash
.venv/bin/uvicorn src.backend.main:app --reload
```

Open http://127.0.0.1:8000. The API docs are at http://127.0.0.1:8000/api/docs.

The frontend has no build step: edit files in `src/frontend` and reload the page.

To run the whole stack in Docker (as on the server) use `docker compose up -d --build`. Set
`APP_PORT` in `.env` if port 8000 is taken.

## Tests

```bash
.venv/bin/pytest
```

The tests run the real FastAPI app and database code against SQLite in memory, so they need
no running database and no `.env`. To run them against PostgreSQL, point
`TEST_DATABASE_URL` at an **empty** database that may be wiped:

```bash
docker compose exec db createdb -U formelx formelx_test
TEST_DATABASE_URL=postgresql+asyncpg://formelx:<password>@localhost:5432/formelx_test .venv/bin/pytest
```

## Changing the schema

1. Change the tables in `src/backend/tables.py`.
2. Generate a migration and review it:
   ```bash
   .venv/bin/alembic revision --autogenerate -m "Add something"
   ```
3. Apply it with `.venv/bin/alembic upgrade head`. `alembic check` reports whether the tables
   and the migrations still match.

The app container applies migrations itself on every start.

## Translations

Translations are JSON files in `src/frontend/locales/` (`de`, `en`, `es`, `fr`, `nl`).

- Keys are snake_case ids (`"add_category"`), not English text.
- When you add a key, add it to **all five** files. Missing keys fall back to English, then
  to the key itself.
- Many values have intentional leading/trailing spaces because strings are concatenated,
  e.g. `tj("select", "category")` → `"Wähle Kategorie"`. Keep them.
- Element names from the database (`hydrogen`, …) are translation keys too.

To add a language, add `<code>.json` and register it in `LANGUAGES` in
`src/frontend/js/i18n.js`.

## Conventions

- Backend: one router per resource in `src/backend/routers`; database access only through
  `Database` in `database.py`; schema in `tables.py` plus an Alembic migration; request
  validation in `schemas.py`; ownership checks via the dependencies in `security.py`.
- Frontend: views in `js/views` render into `<main>` with the `h()` helper from `js/ui.js`.
  All user-visible text goes through `t()`/`tj()`. State changes that affect the whole page
  call `notify()` from `store.js`, which re-renders the header and the current view.
- Commit messages are short imperative English sentences.
