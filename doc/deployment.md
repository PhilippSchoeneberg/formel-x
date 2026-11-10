# Deployment

FormelX runs on a server behind a shared **Caddy** reverse proxy. A reverse proxy is the one
web server that receives all requests from the internet and forwards each to the right project.
Caddy terminates TLS: it holds the HTTPS certificates (from Let's Encrypt, renewed
automatically), redirects `http://` to `https://`, and talks to the projects over plain HTTP
inside a private Docker network called `web`.

```
Browser ──HTTPS──▶ Caddy (/opt/proxy, ports 80/443) ──HTTP over "web"──▶ formel-x:8000 ──▶ formel-x-db:5432
```

`compose.yaml` defines two containers:

| Container | What | Networks | Published ports |
| --- | --- | --- | --- |
| `formel-x` | FastAPI app and frontend on port 8000 | `web`, `internal` | none |
| `formel-x-db` | PostgreSQL 17 | `internal` (no internet access) | none |

Nothing publishes a port, so the only way in is through Caddy, which always uses HTTPS.

## Configuration (`.env`)

Copy `.env.example` to `.env` next to `compose.yaml` and fill in:

| Variable | Description |
| --- | --- |
| `PUBLIC_HOST` | The domain without `https://`: `formel-x.duckdns.org`. Other `Host` headers get `400`. |
| `POSTGRES_PASSWORD` | Database password. Letters, digits, `-` and `_` only (it's part of a URL). |
| `SESSION_SECRET` | At least 32 random characters; signs the login cookie. Changing it logs everyone out. |
| `SECURE_COOKIES` | `true` on the server (default): the login cookie is only sent over HTTPS. |
| `FORWARDED_ALLOW_IPS` | Optional, default `*`. See "Proxy headers" below. |

Generate random values with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`.
`.env` is in `.gitignore`; never commit it.

## Caddy site block

Add this to `/opt/proxy/Caddyfile`, then reload Caddy:

```caddyfile
formel-x.duckdns.org {
	encode zstd gzip
	header Strict-Transport-Security "max-age=31536000"
	reverse_proxy formel-x:8000
}
```

- `encode zstd gzip` compresses responses.
- `Strict-Transport-Security` (HSTS) tells browsers to use only HTTPS for this domain for a
  year. The app doesn't send it itself, so it appears exactly once.
- `reverse_proxy formel-x:8000` forwards to the container by name over the `web` network.
  Caddy keeps the original `Host` header and adds `X-Forwarded-For`, `X-Forwarded-Proto` and
  `X-Forwarded-Host`.

The app does no TLS and no redirects of its own (they would loop behind Caddy).

## Proxy headers

uvicorn runs with `--proxy-headers`: it takes the visitor's address from `X-Forwarded-For` and
the original scheme (`https`) from `X-Forwarded-Proto`, but only from the addresses in
`FORWARDED_ALLOW_IPS`. The default `*` trusts any container that can reach the app, which is
only containers on the `web` network because no port is published. To trust only the `web`
network's address range, look it up and put it in `.env`:

```bash
docker network inspect web --format '{{(index .IPAM.Config 0).Subnet}}'   # e.g. 172.18.0.0/16
```

```
FORWARDED_ALLOW_IPS=172.18.0.0/16
```

The visitor's address matters for the login rate limits.

## Deploy and update

```bash
git clone -b main https://github.com/PhilippSchoeneberg/formel-x.git /opt/formel-x
cd /opt/formel-x
cp .env.example .env && nano .env
docker compose up -d --build
```

The image is built on the server for its own architecture (arm64 on Oracle Ampere). The app
container runs the database migrations on every start.

To update:

```bash
cd /opt/formel-x && git pull && docker compose up -d --build
```

Check the state with `docker compose ps` (both containers should be `healthy`) and
`docker compose logs -f app`.

## Moving the existing data to the server

The simplest way is to copy your local database (which already holds the imported Supabase data):

```bash
# On your computer
docker exec formel-x-db-1 pg_dump -U formelx -Fc formelx > formelx.dump
scp formelx.dump <user>@<server>:/tmp/

# On the server, after the first `docker compose up -d --build`
docker compose stop app
docker exec -i formel-x-db pg_restore -U formelx -d formelx --clean --if-exists < /tmp/formelx.dump
docker compose start app
rm /tmp/formelx.dump
```

Alternatively run the Supabase import on the server inside the app container (only on a fresh
database):

```bash
docker compose exec -e SUPABASE_URL=https://<ref>.supabase.co -e SUPABASE_KEY=<key> app \
  python -m src.backend.import_supabase
```

## Backups

All persistent data (accounts with password hashes, groups, categories, compounds, questions
and element lists) is in the named Docker volume `formel-x_db-data`, used by `formel-x-db`.
Back it up regularly and keep copies on another machine:

```bash
# Dump (e.g. nightly from cron)
docker exec formel-x-db pg_dump -U formelx -Fc formelx > formelx-$(date +%F).dump

# Restore into the running database
docker exec -i formel-x-db pg_restore -U formelx -d formelx --clean --if-exists < formelx-2026-11-10.dump
```

Never run `docker compose down -v` on the server: `-v` deletes the database volume.

## Security checklist

- `SESSION_SECRET`: long random value (the app refuses anything under 32 characters).
- `SECURE_COOKIES=true`; the login cookie is `Secure; HttpOnly; SameSite=Lax`.
- `PUBLIC_HOST` set to the real domain.
- Delete the old Supabase project after moving the data; its public key is in this repository's history.
- Merge Dependabot's pull requests regularly and keep the server's OS, Docker and Caddy up to date.
- Turn on **Private vulnerability reporting** in the repository settings (Security → Advanced
  Security) so the link in `SECURITY.md` works.

## Login protection

Failed logins are limited to 5 per email address and 20 per IP address within 15 minutes,
registrations to 5 per IP address per hour, and group-name lookups to 30 per IP per minute
(`src/backend/rate_limit.py`). Further attempts get `429 Too Many Requests` with a
`Retry-After` header. The counters live in the app process, so they reset on restart and don't
work across several app instances (that would need Redis).

## Release flow

`main` holds released versions and is what the server clones. Merge `development` into `main`
through a pull request, then on the server: `git pull && docker compose up -d --build`.
