# Development

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env   # then fill in SUPABASE_URL, SUPABASE_KEY and SESSION_SECRET
```

For local development set `SECURE_COOKIES=false` in `.env`, otherwise the browser won't
send the login cookie over plain `http://`.

## Run

From the repository root:

```bash
.venv/bin/uvicorn src.backend.main:app --reload
```

Open http://127.0.0.1:8000. The API docs are at http://127.0.0.1:8000/api/docs.

The frontend has no build step: edit files in `src/frontend` and reload the page.

## Tests

```bash
.venv/bin/pytest
```

The tests run the real FastAPI app against `tests/fake_db.py`, an in-memory stand-in for
Supabase, so they need neither network access nor a `.env` file.

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
  `Database` in `database.py`; request validation in `schemas.py`; ownership checks via the
  dependencies in `security.py`.
- Frontend: views in `js/views` render into `<main>` with the `h()` helper from `js/ui.js`.
  All user-visible text goes through `t()`/`tj()`. State changes that affect the whole page
  call `notify()` from `store.js`, which re-renders the header and the current view.
- Commit messages are short imperative English sentences.
