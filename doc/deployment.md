# Deployment

FormelX runs as two containers defined in `docker-compose.yml`:

- `db` – PostgreSQL 17 with its data in the Docker volume `db-data`. Its port is only bound
  to `127.0.0.1` on the server.
- `app` – FastAPI serving the API and the frontend on port 8000. It applies the database
  migrations (`alembic upgrade head`) every time it starts.

You need a server with Docker and a persistent disk, e.g. a small VPS.

## Configuration

Create `.env` next to `docker-compose.yml` (see `.env.example`):

| Variable | Description |
| --- | --- |
| `POSTGRES_PASSWORD` | Password of the database user `formelx`. Pick a long random one. |
| `SESSION_SECRET` | Long random string that signs the login cookie. Changing it logs everyone out. |
| `SECURE_COOKIES` | `true` (default) in production, so the cookie is only sent over HTTPS. |
| `APP_PORT` | Optional host port for the app (default 8000). |

`DATABASE_URL` is set by `docker-compose.yml` for the app container; you only need it in
`.env` for local development and for the import script.

## Start

```bash
docker compose up -d --build
```

Put a reverse proxy that terminates HTTPS in front of port 8000 (e.g. Caddy or nginx).
Uvicorn runs with `--proxy-headers`.

To update: pull the new code and run `docker compose up -d --build` again.

## Importing the data from Supabase (once)

The old data lives in the Supabase project. To move it over:

1. Start only the database and create the tables:
   ```bash
   docker compose up -d db
   DATABASE_URL=postgresql+asyncpg://formelx:<POSTGRES_PASSWORD>@localhost:5432/formelx .venv/bin/alembic upgrade head
   ```
2. Put `SUPABASE_URL` and `SUPABASE_KEY` in `.env` and run the import:
   ```bash
   DATABASE_URL=postgresql+asyncpg://formelx:<POSTGRES_PASSWORD>@localhost:5432/formelx .venv/bin/python -m src.backend.import_supabase
   ```
   It copies accounts (with their password hashes, so logins keep working), groups,
   categories, compounds, questions and element lists, keeps all ids, and refuses to run if
   the database already has accounts or groups.
3. Start the app: `docker compose up -d --build`.
4. When everything looks right, remove `SUPABASE_URL`/`SUPABASE_KEY` from `.env` and pause or
   delete the Supabase project. Its anon key is in this repository's history, so anyone could
   read that project's tables, including password hashes, until it is deleted.

## Backups

All data is in the `db-data` volume. Back it up regularly and store the copies on another
machine.

```bash
# Dump (e.g. nightly from cron)
docker compose exec -T db pg_dump -U formelx -Fc formelx > formelx-$(date +%F).dump

# Restore into an empty database
docker compose exec -T db pg_restore -U formelx -d formelx --clean --if-exists < formelx-2026-11-10.dump
```

Never run `docker compose down -v` on the server: `-v` deletes the database volume.

## Release flow

`main` holds released versions. Merge `development` into `main` through a pull request,
then deploy from `main`.
