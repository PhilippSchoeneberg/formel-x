# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

**FormelX** is a chemistry learning web app. The frontend is plain HTML/CSS/JS (ES modules, no build step, no framework); the backend is Python **FastAPI**, which also serves the frontend. Data lives in the app's own **PostgreSQL** database (Docker), accessed with SQLAlchemy Core + asyncpg; the schema is managed with Alembic.

Learning modes:

- **Elements** – periodic table. Remembering mode shows it (owners click elements to add/remove them from the group's learning list); learning mode hides symbols and asks "Where is X?".
- **Compounds** – multiple choice, formula → name or name → formula.
- **Questions** – free-form multiple choice.

Content is organised into **groups** (courses). A logged-in account *owns* groups and edits their content. Visitors without an account add existing groups by exact name (saved in `localStorage`) and only learn.

Until November 2026 this was a Kivy/Android app (never published) on Supabase; that code is gone from the tree but lives in git history. `src/backend/import_supabase.py` copies the old Supabase data over once.

## Running

```bash
uv sync                                                                   # install deps (incl. dev group)
cp .env.example .env                                                      # fill in values
docker compose up -d db                                                   # PostgreSQL
uv run alembic upgrade head                                               # create/upgrade tables
uv run uvicorn src.backend.main:app --reload                              # http://127.0.0.1:8000
uv run playwright install chromium                                        # once, for browser tests
uv run pytest                                                             # all tests (-m 'not e2e' skips the browser)
```

- Run uvicorn from the repo root (the import path is `src.backend.main:app`). File paths inside the app are resolved from `config.py`, not the CWD.
- `.env` needs `POSTGRES_PASSWORD`, `DATABASE_URL` (`postgresql+asyncpg://formelx:<pw>@localhost:5432/formelx`), `SESSION_SECRET`; set `SECURE_COOKIES=false` for local http. Never commit `.env` and never print secrets.
- Tests (`tests/conftest.py`) run the real app and `Database` on SQLite in memory (tables via `metadata.create_all`); set `TEST_DATABASE_URL` to run them on an empty, wipeable Postgres database. Add tests when changing the API. Keep queries portable between SQLite and Postgres. `tests/e2e/` has Playwright browser tests for the main flows (`-m 'not e2e'` skips them).
- Full stack: `docker compose up -d --build` (app container runs `alembic upgrade head` on start). `APP_PORT` overrides host port 8000. Never use `docker compose down -v` on real data (deletes the DB volume).

## Layout

```
src/backend/    main.py (entry), app.py (create_app), config.py, database.py, tables.py, elements_data.py, security.py, schemas.py, routers/, migrations/, import_supabase.py
src/frontend/   index.html, css/style.css, js/{main,api,store,i18n,ui,dialogs,formula}.js, js/views/, locales/, assets/
tests/          pytest (conftest.py, test_api.py)
doc/            architecture.md, api.md, development.md, deployment.md
```

See `doc/architecture.md` for the full picture and `doc/api.md` for every endpoint.

## Backend conventions

- All DB access goes through `Database` (`database.py`), one async method per query (each its own transaction), returning plain dicts.
- `DatabaseConnectionError` → 503 `connection_error`; other DB errors → `DatabaseError` → 502 (logged); unique violations → `DatabaseConflictError`.
- Every endpoint declares a `response_model` from `schemas.py`; routes return DB dicts and the model filters them. Add the model when adding an endpoint.
- Login/registration go through `RateLimiter` (`rate_limit.py`, `app.state.rate_limiter`). New passwords need `MIN_PASSWORD_LENGTH` (8) characters; login doesn't check it.
- Config is `pydantic-settings` (`config.py`): `Settings`, `DatabaseSettings`, `SupabaseSettings`; env vars win over `.env`.
- Dependencies: `pyproject.toml` + `uv.lock` (uv). Use `uv add`, never pip/requirements files.
- Errors use short `detail` codes (`group_exists`, `invalid_credentials`, `not_group_owner`, …) that the frontend maps to translated messages. Don't return English sentences.
- Auth: bcrypt via the `bcrypt` package (old passlib hashes verify fine). Login stores `account_id` in Starlette's signed, HTTP-only session cookie. Use the dependencies in `security.py`: `require_account_id`, `get_group_or_404`, `get_owned_group`, `ensure_owner`.
- Passwords are stripped before hashing/verifying (the old app did this; keep it for existing accounts). Max 72 bytes.
- Categories store `type` as int in the DB (compound=0, question=1) but the API uses `"compound"`/`"question"` (`CategoryType` in `schemas.py`). Difficulty is `"easy"|"medium"|"hard"` (also translation keys).
- Compounds and questions share one router factory (`routers/entries.py`): one correct + 2 required + 2 optional wrong answers; the category must belong to the same group and type.
- Never return `accounts.password` from an endpoint.

## Frontend conventions

- Hash router in `js/main.js`: `#/`, `#/elements`, `#/compounds`, `#/questions`, `#/<kind>/learn?category=&difficulty=`. Views are `render*(view, …)` functions in `js/views/` that rebuild `<main>`.
- Build DOM with `h(tag, attrs, ...children)` from `js/ui.js` (never `innerHTML` with user content). Dialogs: `openDialog`, `messageDialog`, `confirmDialog`, and the forms in `js/dialogs.js`.
- Global state is `state` in `js/store.js`; after a change that affects the page, call `notify()` (re-renders header + current view). Preferences persist in `localStorage` key `formelx`.
- API calls go through `api` in `js/api.js`, which throws `ApiError` (`status`, `detail`, `isConnectionError`). Use `showError(error)` for unexpected failures.
- Formulas use LaTeX-like notation, rendered with `formulaToUnicode` (`H_2O` → `H₂O`, `SO_4^{2-}` → `SO₄²⁻`).
- Styling: one `css/style.css` with CSS custom properties; light/dark via `prefers-color-scheme` and `data-theme` on `<html>`. Correct/wrong answers use `--good`/`--bad` tokens.
- Keep it dependency-free: no npm, no bundler, no CDN scripts.
- Security rules (strict CSP in `src/backend/middleware.py`, tests in `tests/test_security.py`):
  - No inline `<script>`/`<style>`, no `style="…"` attributes, no event-handler attributes, no third-party URLs. Pass `style` to `h()` (it uses `element.style.cssText`).
  - Insert user content only as text (`h()`/`textContent`), never via `innerHTML`.
  - New endpoints get rate limits if they can be used to guess or brute-force something (`rate_limit.py`).
- Accessibility rules (covered by `tests/e2e/test_accessibility.py`):
  - Every view has exactly one `<h1>`; the router focuses it after navigation and sets `document.title` from it.
  - Re-rendering must not drop focus: restore it (see `renderHeader`, `renderElements(view, { focus })`, `renderQuiz(…, { focusPrompt })`). Don't `disable` a button the user just pressed; use `aria-disabled`.
  - Never show state by color alone: add a mark (✓/✗, dot) and text for screen readers (`.sr-only`, accessible names).
  - Form errors: `field()`/`selectField()` link hint and error via `aria-describedby`; call `focusFirstInvalid(form)` after validation fails (`formDialog` does it).
  - The periodic table is one Tab stop with arrow-key navigation (roving tabindex); in practice mode cells are named by position, never by element.
  - Use `uid()` for ids, never fixed ids (dialogs can stack).

## Internationalisation

- All visible strings go through `t("key", params)` (`js/i18n.js`). Keys are snake_case ids, not English, and each value is a **complete** phrase or sentence with named placeholders: `"where_is": "Where is {element}?"` → `t("where_is", { element })`.
- Never build a sentence by joining several keys or by concatenating text around a translation: word order, articles and gender differ per language. Add a new key with placeholders instead.
- Tone: informal (du / tú / tu / je), short labels, sentence case in en. Quote marks per language: “…” en, „…“ de, «…» es, « … » fr, ‘…’ nl.
- When adding a key, add it to **all five** `src/frontend/locales/{de,en,es,fr,nl}.json`. Element names from the DB (`hydrogen`, …) are keys too; inside sentences they're lowercased except in German (see `views/elements.js`).

## Database

- Tables: `accounts`, `groups`, `elements`, `elements_to_groups`, `categories`, `compounds`, `questions`, defined in `src/backend/tables.py`. Content tables are scoped by `group_id`. Column names match the old Supabase schema.
- Schema changes: edit `tables.py`, then `alembic revision --autogenerate -m "..."`, review the file in `src/backend/migrations/versions/`, and check `alembic check` is clean. Never edit an applied migration. The first migration seeds the elements from `elements_data.py`.
- Ids are `BigInteger` with a SQLite `Integer` variant (`Id` in `tables.py`) so tests autoincrement.
- The DB stores lanthanides/actinides as group 3; the frontend lays out the f-block from hard-coded symbol lists in `js/views/elements.js`.

## Known gotchas

- `.idea/` (IDE config) is ignored by git.
- The old Supabase anon key is in git history (from the Android app). Treat it as public; the Supabase project should be deleted after the import.

## Git

Feature-branch workflow:

- **`development`** is the default branch and the integration branch. It changes **only through merged pull requests** from feature branches. Never commit or push to it directly.
- **`main`** contains released versions only. It is updated by a pull request from `development` when a release is made; deploy from `main`.
- **Feature branches** start from the latest `development` and are named by type: `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>`. Open the PR against `development`.
  ```bash
  git switch development && git pull
  git switch -c feature/<short-name>
  # ...commit...
  git push -u origin feature/<short-name>
  gh pr create --base development
  ```
- CI (`.github/workflows/tests.yml`) runs the `tests` and `docker-build` jobs on every PR into `development`/`main`; the branch rulesets require both to pass before merging. Run `uv run pytest` locally before pushing. Keep the job names stable: they're the required check names.
- Urgent fixes to a release: branch `hotfix/<name>` from `main`, PR into `main`, then merge `main` back into `development`.
- Commit messages are short imperative English sentences (e.g. "Fix the refreshing of categories after creation.").
