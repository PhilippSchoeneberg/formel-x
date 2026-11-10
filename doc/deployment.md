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
| `DB_PORT` | Optional host port for PostgreSQL on `127.0.0.1` (default 5432). |

`DATABASE_URL` is set by `docker-compose.yml` for the app container; you only need it in
`.env` for local development and for the import script.

## Start

```bash
docker compose up -d --build
```

The app's port is bound to `127.0.0.1` only. Put a reverse proxy that terminates HTTPS in front of it
(e.g. Caddy or nginx); never expose port 8000 directly, or passwords and the login cookie would
travel unencrypted. With `SECURE_COOKIES=true` (the default) the app also sends HSTS, so browsers
only ever use HTTPS for the site.
Uvicorn runs with `--proxy-headers`, but only trusts `X-Forwarded-For` from the addresses in
`FORWARDED_ALLOW_IPS` (default `127.0.0.1`). If the proxy reaches the container from another
address (e.g. the Docker bridge), add `FORWARDED_ALLOW_IPS=<proxy address>` to the app's
environment. Otherwise every visitor looks like the proxy, and the login rate limit is shared
by everyone.

The proxy must pass the public host name, either as `Host` (Caddy does this by default; in nginx
use `proxy_set_header Host $host;`) or as `X-Forwarded-Host`. Otherwise the cross-site check
rejects every form submission with `403 cross_origin_request`.

## Security checklist

- `SESSION_SECRET`: long random value (the app refuses anything under 32 characters), different
  from any other environment. Changing it logs everyone out.
- `SECURE_COOKIES=true` and HTTPS only.
- `FORWARDED_ALLOW_IPS` set to the proxy's address if it isn't `127.0.0.1` (otherwise rate limits
  see every visitor as the proxy).
- Delete the old Supabase project after the import; its public key is in this repository's history.
- Merge Dependabot's pull requests regularly and keep the server's OS and Docker up to date.
- Turn on **Private vulnerability reporting** in the repository settings (Security → Advanced
  Security) so the link in `SECURITY.md` works.

## Login protection

Failed logins are limited to 5 per email address and 20 per IP address within 15 minutes,
and registrations to 5 per IP address per hour (`src/backend/rate_limit.py`). Further attempts
get `429 Too Many Requests` with a `Retry-After` header. The counters live in the app process,
so they reset on restart and don't work across several app instances (that would need Redis).

To update: pull the new code and run `docker compose up -d --build` again.

## Importing the data from Supabase (once)

The old data lives in the Supabase project. To move it over:

1. Start only the database and create the tables:
   ```bash
   docker compose up -d db
   uv run alembic upgrade head
   ```
2. Put `SUPABASE_URL` and `SUPABASE_KEY` in `.env` and run the import:
   ```bash
   uv run python -m src.backend.import_supabase
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
