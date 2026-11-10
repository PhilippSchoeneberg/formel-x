"""Browser tests: the real app on a temporary SQLite database, driven by Playwright.

Run once before the first time:  uv run playwright install chromium
"""

import asyncio
import socket
import threading

import pytest
import uvicorn
from sqlalchemy import insert

from src.backend.app import create_app
from src.backend.config import Settings
from src.backend.database import Database
from src.backend.elements_data import ELEMENTS
from src.backend.security import hash_password
from src.backend.tables import elements, metadata


OWNER_EMAIL = "owner@example.test"
OWNER_PASSWORD = "e2e-owner-password"


def pytest_collection_modifyitems(items):
    for item in items:
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)


async def _seed(db):
    async with db.engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.execute(insert(elements), [
            {"symbol": s, "name": n, "system_group": g, "system_period": p} for s, n, g, p in ELEMENTS
        ])
    owner = await db.create_account(OWNER_EMAIL, hash_password(OWNER_PASSWORD))
    group = await db.create_group("Demo", owner["id"])
    for symbol in ("H", "O", "Fe"):
        await db.add_element_to_group(group["id"], symbol)
    acids = await db.create_category(group["id"], "Acids", 0)
    basics = await db.create_category(group["id"], "Basics", 1)
    await db.create_entry("compounds", {
        "correct_name": "Sulfuric acid", "wrong_name1": "Sulfurous acid", "wrong_name2": "Sulfate",
        "correct_formula": "H_2SO_4", "wrong_formula1": "H_2SO_3", "wrong_formula2": "SO_4^{2-}",
        "difficulty": "easy", "category_id": acids["id"], "group_id": group["id"],
    })
    await db.create_entry("questions", {
        "question": "How many protons does a carbon atom have?", "correct_answer": "6",
        "wrong_answer1": "12", "wrong_answer2": "4",
        "difficulty": "easy", "category_id": basics["id"], "group_id": group["id"],
    })


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    """Starts the app in a background thread and returns its URL (also used by pytest-playwright)."""
    url = f"sqlite+aiosqlite:///{tmp_path_factory.mktemp('e2e') / 'formelx.db'}"
    db = Database(url)
    app = create_app(Settings(database_url=url, session_secret="e2e-secret", secure_cookies=False), db=db)
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))

    async def run():
        await _seed(db)
        try:
            await server.serve()
        finally:
            await db.close()

    thread = threading.Thread(target=lambda: asyncio.run(run()), daemon=True)
    thread.start()
    for _ in range(200):
        if server.started:
            break
        threading.Event().wait(0.05)
    else:
        raise RuntimeError("The test server didn't start.")

    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=10)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    # English UI regardless of the machine's language.
    return {**browser_context_args, "locale": "en-US"}
