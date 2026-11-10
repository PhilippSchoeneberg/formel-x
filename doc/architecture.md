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
    config.py        Settings (pydantic-settings) from environment variables / .env
    database.py      Async data access (SQLAlchemy Core), one method per query
    tables.py        Table definitions (the schema)
    elements_data.py The 118 elements, seeded by the first migration
    migrations/      Alembic migrations (alembic.ini is in the repository root)
    import_supabase.py  One-time import from the old Supabase project
    security.py      bcrypt hashing, session login, owner checks (FastAPI dependencies)
    rate_limit.py    In-memory rate limits for login and registration
    schemas.py       Pydantic request and response models
    routers/         auth, groups, elements, categories, entries (compounds + questions)
  frontend/
    index.html       App shell
    css/style.css    All styles, themed with CSS custom properties (light/dark)
    js/main.js       Boot, header, hash router
    js/api.js        fetch wrapper for /api
    js/store.js      App state + localStorage preferences
    js/i18n.js       Translation loading and t() with {placeholders}
    js/ui.js         DOM helper h(), icons, dialogs, form fields
    js/dialogs.js    Login, group, category, compound/question dialogs
    js/formula.js    H_2O → H₂O notation
    js/views/        home, elements (periodic table), menu (categories), quiz
    locales/         de/en/es/fr/nl JSON translations
    assets/          Logo and the Roboto font
tests/               pytest API tests (SQLite in memory, or Postgres via TEST_DATABASE_URL)
  e2e/               Playwright browser tests
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
- New passwords need at least 8 characters; login doesn't check this, so older accounts keep working.
- Failed logins and registrations are rate-limited (`429` with `Retry-After`).
- Every endpoint declares a Pydantic `response_model`, so responses only ever contain the
  listed fields (never password hashes) and `/api/docs` shows exact types.

## Frontend

- Plain ES modules, no build step and no framework. The browser loads them directly.
- Hash routes: `#/`, `#/elements`, `#/compounds`, `#/questions`,
  `#/compounds/learn?category=<id>&difficulty=<d>` and the same for questions.
- Preferences (theme, language, selected group, difficulty, compound quiz direction, the
  visitor's saved groups) live in `localStorage` under the key `formelx`.
- Translations are keyed by snake_case ids. Each value is a full sentence with named
  placeholders (`t("where_is", { element })`), so every language can use its own grammar.

## Security

- **Passwords:** bcrypt; at least 8 characters for new accounts; login and registration are
  rate-limited; a login with an unknown email runs a dummy bcrypt check so response times don't
  reveal which addresses have an account.
- **Session:** signed, HTTP-only cookie (`SameSite=Lax`, `Secure` in production). The signing
  secret must be at least 32 characters.
- **CSRF:** besides `SameSite=Lax`, `SameOriginMiddleware` rejects API writes whose `Origin` or
  `Sec-Fetch-Site` shows another site (`403 cross_origin_request`). There's no CORS, so other
  sites can't read API responses either.
- **XSS:** the frontend only inserts user content as text (`h()` has no raw-HTML option). A strict
  Content-Security-Policy allows only the site's own scripts, styles, fonts and requests; dynamic
  styles go through the CSSOM (`element.style`), which CSP permits.
- **Headers** on every response: CSP, `X-Content-Type-Options`, `X-Frame-Options`/`frame-ancestors`
  (no framing), `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`,
  `Cross-Origin-Resource-Policy`, and HSTS when `SECURE_COOKIES` is on.
- **Abuse limits:** request bodies over 64 KiB get `413`; group-name lookups are limited to 30 per
  minute per IP; `/groups/lookup` takes at most 100 ids.
- **SQL injection:** all queries go through SQLAlchemy with bound parameters.
- **Dependencies:** pinned in `uv.lock`; Dependabot opens update PRs, and CI tests them.

Known limits: group content is readable by anyone who knows a group's id or name (groups are
shared by name on purpose), and sessions can't be revoked server-side before they expire.

## Accessibility

Target: WCAG 2.2 AA. axe reports no violations on any screen in either theme.

- Each page has one `<h1>`; after navigation focus moves to it and the browser tab title
  follows it ("Compounds – FormelX").
- Everything works with the keyboard. The periodic table is a single Tab stop; the arrow keys,
  Home and End move between elements. In practice mode the cells are announced by position
  ("Period 4, group 8"), so screen reader users can play too.
- Right/wrong and "in the practice list" are shown with color **and** a ✓/✗ mark or a dot, plus
  text for screen readers. Windows high-contrast mode gets outlines instead of backgrounds.
- Answer feedback and the current question are announced through live regions; focus moves to
  the next question after a correct answer and stays on a wrong one.
- Form errors are linked to their fields (`aria-describedby`, `aria-invalid`) and focus jumps to
  the first invalid field.
- Animations are turned off for `prefers-reduced-motion`.

## Errors

- Database unreachable → API answers `503 {"detail": "connection_error"}`; the frontend shows
  the translated connection error.
- Other database errors → `502 {"detail": "database_error"}`; they are logged on the server.
- Validation and business errors use short `detail` codes such as `group_exists`,
  `invalid_credentials` or `not_group_owner`; see [api.md](api.md).
