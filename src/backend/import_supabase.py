"""One-time import of all data from the old Supabase project into the PostgreSQL database.

Usage (from the repository root, after `alembic upgrade head`):

    uv run python -m src.backend.import_supabase

SUPABASE_URL and SUPABASE_KEY (the source) and DATABASE_URL (the target) come from the
environment or .env. The import keeps all ids, dates and
password hashes, so existing accounts can log in as before. It refuses to run when the target
already has accounts or groups, and runs in a single transaction: either everything is
imported or nothing.
"""

import asyncio
import sys
from datetime import datetime

import httpx
from sqlalchemy import func, insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from .config import SupabaseSettings, database_url
from .tables import accounts, categories, compounds, elements, elements_to_groups, groups, questions


PAGE_SIZE = 1000

# Tables in insert order, with the column that orders the pages.
TABLES = [
    (accounts, "id"),
    (groups, "id"),
    (categories, "id"),
    (compounds, "id"),
    (questions, "id"),
    (elements, "symbol"),
    (elements_to_groups, "group_id"),
]


async def fetch_table(client, table, order):
    rows = []
    while True:
        response = await client.get(f"/{table.name}", params={
            "select": "*", "order": f"{order}.asc", "limit": PAGE_SIZE, "offset": len(rows),
        })
        response.raise_for_status()
        page = response.json()
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows


def _parse_date(value):
    if not value:
        return None
    # PostgREST sends e.g. "2025-10-15T19:48:00.54948" (or with a timezone suffix).
    value = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        main, _, fraction = value.partition(".")
        digits = "".join(ch for ch in fraction if ch.isdigit())[:6].ljust(6, "0")
        parsed = datetime.fromisoformat(f"{main}.{digits}")
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def _clean(table, row):
    """Keeps the known columns and converts dates."""
    data = {column.name: row.get(column.name) for column in table.columns}
    if "date" in data:
        data["date"] = _parse_date(data["date"])
        if data["date"] is None:
            del data["date"]  # use the database default
    return data


def prepare(source):
    """Drops rows whose references are missing, so the import can't fail halfway."""
    skipped = {}

    def keep(name, rows, condition):
        kept = [row for row in rows if condition(row)]
        if len(kept) != len(rows):
            skipped[name] = len(rows) - len(kept)
        return kept

    account_ids = {row["id"] for row in source["accounts"]}
    source["groups"] = keep("groups", source["groups"], lambda r: r["owner_id"] in account_ids)
    group_ids = {row["id"] for row in source["groups"]}
    source["categories"] = keep("categories", source["categories"], lambda r: r["group_id"] in group_ids)
    category_ids = {row["id"] for row in source["categories"]}
    for name in ("compounds", "questions"):
        source[name] = keep(name, source[name], lambda r: r["group_id"] in group_ids and r["category_id"] in category_ids)
    symbols = {row["symbol"] for row in source["elements"]}
    source["elements_to_groups"] = keep(
        "elements_to_groups", source["elements_to_groups"], lambda r: r["group_id"] in group_ids and r["symbol"] in symbols
    )
    return skipped


async def main():
    try:
        source_settings = SupabaseSettings()
        target_url = database_url()
    except ValueError as e:
        sys.exit(f"Missing configuration (see the docstring of this script):\n{e}")
    supabase_url = source_settings.supabase_url.strip().rstrip("/")
    supabase_key = source_settings.supabase_key.strip()

    headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
    async with httpx.AsyncClient(base_url=f"{supabase_url}/rest/v1", headers=headers, timeout=30) as client:
        source = {table.name: await fetch_table(client, table, order) for table, order in TABLES}
    skipped = prepare(source)

    engine = create_async_engine(target_url)
    try:
        async with engine.begin() as connection:
            for table in (accounts, groups):
                count = (await connection.execute(select(func.count()).select_from(table))).scalar_one()
                if count:
                    sys.exit(f"The target database already has {count} rows in '{table.name}'. "
                             "The import only runs on a fresh database (alembic upgrade head, nothing else).")

            # The migration seeds the elements; add any the old project had in addition.
            existing = set((await connection.execute(select(elements.c.symbol))).scalars())
            missing = [_clean(elements, row) for row in source["elements"] if row["symbol"] not in existing]
            if missing:
                await connection.execute(insert(elements), missing)

            for table, _order in TABLES:
                if table is elements:
                    continue
                rows = [_clean(table, row) for row in source[table.name]]
                if rows:
                    await connection.execute(insert(table), rows)

            # Continue the id sequences after the imported ids.
            if connection.dialect.name == "postgresql":
                for table in (accounts, groups, categories, compounds, questions):
                    await connection.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {table.name}), 1), "
                        f"(SELECT MAX(id) FROM {table.name}) IS NOT NULL)"
                    ))
    finally:
        await engine.dispose()

    print("Imported:")
    for table, _order in TABLES:
        note = f" (+{len(missing)} new)" if table is elements and missing else ""
        print(f"  {table.name}: {len(source[table.name])}{note}")
    for name, count in skipped.items():
        print(f"  Skipped {count} row(s) in {name} with missing references.")


if __name__ == "__main__":
    asyncio.run(main())
