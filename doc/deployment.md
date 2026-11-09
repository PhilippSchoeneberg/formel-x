# Deployment

FormelX runs as one container: FastAPI serves the API and the static frontend on port 8000.

## Configuration

Set these environment variables (see `.env.example`):

| Variable | Description |
| --- | --- |
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `SUPABASE_KEY` | The **service_role** key. Server-side only; never put it in the frontend. |
| `SESSION_SECRET` | Long random string that signs the login cookie. Changing it logs everyone out. |
| `SECURE_COOKIES` | `true` (default) in production, so the cookie is only sent over HTTPS. |

## Docker

```bash
docker build -t formelx .
docker run -p 8000:8000 --env-file .env formelx
```

Put the container behind a reverse proxy or platform that terminates HTTPS (e.g. Fly.io,
Render, Railway, or nginx/Caddy on a VPS). Uvicorn runs with `--proxy-headers`.

## Database

The schema is in `src/backend/sql/setup.sql` and the periodic table seed in
`src/backend/sql/insert_elements.sql`. Both are already applied to the existing Supabase
project; only run them for a fresh database (`setup.sql` drops the tables first).

### Lock down public access

Until now the Android app used Supabase's public anon key directly, which means anyone with
that key (it is in the app and in this repository's history) can read every table,
including the password hashes in `accounts`.

Once the web app has replaced the Android app:

1. Run `src/backend/sql/lockdown.sql` in the Supabase SQL editor. It enables row level
   security without policies, so the anon key can no longer access any table.
2. Make sure the backend uses the service_role key, which bypasses row level security.
3. Optionally rotate the anon key and the JWT secret in the Supabase dashboard.

Running the lockdown breaks the released Android app (version 4), so plan the switch.

## Release flow

`main` holds released versions. Merge `development` into `main` through a pull request,
then deploy from `main`.
