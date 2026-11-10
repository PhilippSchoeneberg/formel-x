"""Test fixtures: the real FastAPI app on the real database layer.

By default the database is SQLite in memory. Set TEST_DATABASE_URL to a PostgreSQL URL
(e.g. postgresql+asyncpg://formelx:formelx@localhost:5432/formelx_test) to run the same
tests against Postgres. All tables in that database are dropped and recreated per test.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from src.backend.app import create_app
from src.backend.config import Settings, normalize_database_url
from src.backend.database import Database
from src.backend.elements_data import ELEMENTS
from src.backend.tables import elements, metadata


TEST_DATABASE_URL = normalize_database_url(os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite://"))

SETTINGS = Settings(database_url=TEST_DATABASE_URL, session_secret="test-secret-at-least-32-characters-long", secure_cookies=False)


async def _reset(db):
    async with db.engine.begin() as connection:
        await connection.run_sync(metadata.drop_all)
        await connection.run_sync(metadata.create_all)
        await connection.execute(insert(elements), [
            {"symbol": s, "name": n, "system_group": g, "system_period": p} for s, n, g, p in ELEMENTS
        ])


@pytest.fixture
def client():
    db = Database(TEST_DATABASE_URL)
    with TestClient(create_app(SETTINGS, db=db)) as client:
        # Run the setup on the app's event loop so asyncpg connections stay on one loop.
        client.portal.call(_reset, db)
        client.db = db
        yield client
        client.portal.call(db.close)
