"""HTTP hardening: headers, cross-site writes, request size, login timing, secrets."""

import time

import pytest
from pydantic import ValidationError

from src.backend.config import Settings
from src.backend.middleware import MAX_BODY_BYTES
from src.backend.security import hash_password
from tests.test_api import PASSWORD, register


def test_security_headers_on_pages_api_and_errors(client):
    for path in ("/", "/js/main.js", "/api/elements", "/api/groups/999/categories"):
        headers = client.get(path).headers
        csp = headers["content-security-policy"]
        assert "default-src 'self'" in csp and "script-src 'self'" in csp and "frame-ancestors 'none'" in csp
        assert "unsafe-inline" not in csp
        assert headers["x-content-type-options"] == "nosniff"
        assert headers["x-frame-options"] == "DENY"
        assert headers["referrer-policy"] == "same-origin"
    # HSTS belongs to the HTTPS proxy (Caddy), not the app.
    assert "strict-transport-security" not in client.get("/").headers


def test_api_docs_still_work_without_csp(client):
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "content-security-policy" not in response.headers


def test_cross_site_writes_are_rejected(client):
    body = {"email": "x@example.com", "password": PASSWORD}
    response = client.post("/api/auth/register", json=body, headers={"Origin": "https://evil.example"})
    assert response.status_code == 403
    assert response.json() == {"detail": "cross_origin_request"}
    assert client.post("/api/auth/login", json=body, headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403
    assert client.post("/api/auth/login", json=body, headers={"Origin": "null"}).status_code == 403


def test_same_origin_writes_are_allowed(client):
    # The TestClient talks to http://testserver.
    headers = {"Origin": "http://testserver", "Sec-Fetch-Site": "same-origin"}
    response = client.post("/api/auth/register", json={"email": "a@example.com", "password": PASSWORD}, headers=headers)
    assert response.status_code == 201
    # Cross-site *reads* are harmless (no CORS headers, so the attacker can't read them).
    assert client.get("/api/elements", headers={"Origin": "https://evil.example"}).status_code == 200


def test_oversized_bodies_are_rejected(client):
    big = "x" * (MAX_BODY_BYTES + 1)
    response = client.post("/api/auth/login", content=f'{{"email": "a@b.c", "password": "{big}"}}',
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 413
    assert response.json() == {"detail": "request_too_large"}

    def chunks():
        for _ in range(MAX_BODY_BYTES // 1024 + 2):
            yield b"x" * 1024

    response = client.post("/api/auth/login", content=chunks(), headers={"Content-Type": "application/json"})
    assert response.status_code == 413


def test_group_lookup_by_ids_is_capped(client):
    assert client.post("/api/groups/lookup", json={"ids": list(range(101))}).status_code == 422


def test_group_name_guessing_is_rate_limited(client):
    for _ in range(30):
        assert client.get("/api/groups/by-name", params={"name": "guess"}).status_code == 404
    response = client.get("/api/groups/by-name", params={"name": "guess"})
    assert response.status_code == 429


def test_unknown_email_takes_as_long_as_wrong_password(client):
    client.portal.call(client.db.create_account, "real@example.com", hash_password(PASSWORD))

    def timed(email):
        start = time.perf_counter()
        assert client.post("/api/auth/login", json={"email": email, "password": "wrong-password"}).status_code == 401
        return time.perf_counter() - start

    timed("ghost@example.com")  # first call creates the dummy hash
    unknown = min(timed(f"ghost{i}@example.com") for i in range(2))
    known = timed("real@example.com")
    # Both run one bcrypt check; without the dummy check "unknown" would be ~100x faster.
    assert unknown > known * 0.5


def test_session_secret_must_be_long():
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite+aiosqlite://", session_secret="short")


def test_passwords_have_an_upper_bound(client):
    register(client)
    response = client.post("/api/auth/login", json={"email": "owner@example.com", "password": "x" * 1025})
    assert response.status_code == 422


def test_only_allowed_hosts_are_answered():
    from fastapi.testclient import TestClient

    from src.backend.app import create_app
    from src.backend.database import Database
    from tests.conftest import TEST_DATABASE_URL

    settings = Settings(database_url=TEST_DATABASE_URL, session_secret="test-secret-at-least-32-characters-long",
                        secure_cookies=False, allowed_hosts="formelx.example, localhost")
    with TestClient(create_app(settings, db=Database(TEST_DATABASE_URL))) as client:
        assert client.get("/", headers={"Host": "formelx.example"}).status_code == 200
        assert client.get("/", headers={"Host": "localhost:8000"}).status_code == 200
        response = client.get("/", headers={"Host": "attacker.example"})
        assert response.status_code == 400
        # No redirect of any kind from the app: redirects are the proxy's job.
        assert "location" not in response.headers
