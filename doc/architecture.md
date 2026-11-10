# Architecture

FormelX is a single FastAPI server that does two things:

- it serves the static frontend (`src/frontend`) at `/`, and
- it offers a JSON API under `/api` that the frontend calls.

Only the backend talks to the database. The browser never sees database credentials.

```
Browser (HTML/CSS/JS)  ──fetch /api/...──▶  FastAPI (src/backend)  ──SQLAlchemy/asyncpg──▶  PostgreSQL
        ▲                                         │
        └──────────── static files ◀──────────────┘
```

## Directory layout

```
src/
  backend/
    main.py          Entry point for uvicorn: builds the app from environment settings
    app.py           create_app(): middleware, error handlers, routers, static frontend
    config.py        Settings from environment variables / .env
    database.py      Async data access (SQLAlchemy Core), one method per query
    tables.py        Table definitions (the schema)
    elements_data.py The 118 elements, seeded by the first migration
    migrations/      Alembic migrations (alembic.ini is in the repository root)
    import_supabase.py  One-time import from the old Supabase project
    security.py      bcrypt hashing, session login, owner checks (FastAPI dependencies)
    schemas.py       Pydantic request bodies and validation
    routers/         auth, groups, elements, categories, entries (compounds + questions)
  frontend/
    index.html       App shell
    css/style.css    All styles, themed with CSS custom properties (light/dark)
    js/main.js       Boot, header, hash router
    js/api.js        fetch wrapper for /api
    js/store.js      App state + localStorage preferences
    js/i18n.js       Translation loading and t()/tj()
    js/ui.js         DOM helper h(), icons, dialogs, form fields
    js/dialogs.js    Login, group, category, compound/question dialogs
    js/formula.js    H_2O → H₂O notation
    js/views/        home, elements (periodic table), menu (categories), quiz
    locales/         de/en/es/fr/nl JSON translations
    assets/          Logo and the Roboto font
tests/               pytest tests (SQLite in memory, or Postgres via TEST_DATABASE_URL)
doc/                 This documentation
```

## Domain

- **Accounts** own **groups** (courses). Only the owner can change a group and its content.
- Visitors without an account add existing groups by their exact name. Those groups are
  remembered in the browser (`localStorage`), not on the server.
- A group has a list of **elements** to learn, and **categories** of type `compound` or
  `question`. **Compounds** and **questions** belong to a category and have a difficulty
  (`easy`, `medium`, `hard`), one correct answer, two required and two optional wrong answers.

## Authentication

- Passwords are hashed with bcrypt on the server. Hashes created by the old Android app
  (passlib) are compatible.
- After login the server sets a signed, HTTP-only session cookie (`formelx_session`,
  `SameSite=Lax`, 30 days). It only holds the account id. JavaScript never sees a token.
- Write endpoints check that the logged-in account owns the group (`403` otherwise).

## Frontend

- Plain ES modules, no build step and no framework. The browser loads them directly.
- Hash routes: `#/`, `#/elements`, `#/compounds`, `#/questions`,
  `#/compounds/learn?category=<id>&difficulty=<d>` and the same for questions.
- Preferences (theme, language, selected group, difficulty, compound quiz direction, the
  visitor's saved groups) live in `localStorage` under the key `formelx`.
- Translations are keyed by snake_case ids. Many values carry leading/trailing spaces
  because UI strings are built by concatenation (`tj("select", "category")`).

## Errors

- Database unreachable → API answers `503 {"detail": "connection_error"}`; the frontend shows
  the translated connection error.
- Other database errors → `502 {"detail": "database_error"}`; they are logged on the server.
- Validation and business errors use short `detail` codes such as `group_exists`,
  `invalid_credentials` or `not_group_owner`; see [api.md](api.md).
