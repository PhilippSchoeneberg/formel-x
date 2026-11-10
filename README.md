# FormelX

A web app for learning chemistry: find elements in the periodic table, match compound names
and formulas, and answer multiple-choice questions. Content is organised in groups (courses)
that their owners create and edit; anyone can add a group by its name and learn.

- Frontend: plain HTML, CSS and JavaScript (`src/frontend`)
- Backend: Python with FastAPI (`src/backend`), data in PostgreSQL

## Quick start

```bash
python3 -m venv .venv
```
```bash
.venv/bin/pip install -r requirements-dev.txt
```
```bash
cp .env.example .env        # fill in a database password, DATABASE_URL and a session secret
```
```bash
docker compose up -d db     # PostgreSQL in Docker
```
```bash
.venv/bin/alembic upgrade head
```
```bash
.venv/bin/uvicorn src.backend.main:app --reload
```

Then open http://127.0.0.1:8000. To run everything (app and database) in Docker instead, use `docker compose up -d --build`.

Run the tests with `.venv/bin/pytest`.

## Documentation

- [Architecture](doc/architecture.md)
- [API](doc/api.md)
- [Development](doc/development.md)
- [Deployment](doc/deployment.md)

The earlier, unpublished Android app (Kivy) is available in the git history.
