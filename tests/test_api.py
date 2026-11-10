import pytest
from fastapi.testclient import TestClient

from src.backend.app import create_app
from src.backend.config import Settings
from src.backend.database import Database, DatabaseConflictError
from src.backend.security import hash_password, verify_password


COMPOUND = {
    "correct_name": "Water", "wrong_name1": "Hydrogen peroxide", "wrong_name2": "Oxygen",
    "wrong_name3": "", "wrong_name4": None,
    "correct_formula": "H_2O", "wrong_formula1": "H_2O_2", "wrong_formula2": "O_2",
    "difficulty": "easy",
}


PASSWORD = "secret-password"


def register(client, email="owner@example.com", password=PASSWORD):
    response = client.post("/api/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201, response.text
    return response.json()["account"]


def create_group(client, name="Demo"):
    response = client.post("/api/groups", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def test_passlib_hashes_still_verify():
    # Hash created by passlib's bcrypt in the old Kivy app for the password "secret".
    legacy = "$2b$12$8u9MVnGWEAiQ0MNtFPdkuuiC0PfsAlLfsry./aaZBtHCKdrAWO2oq"
    assert verify_password("secret", legacy)
    assert verify_password("secret", hash_password("secret"))
    assert not verify_password("wrong", legacy)
    assert not verify_password("x" * 100, legacy)


def test_register_login_logout(client):
    assert client.get("/api/auth/me").json() == {"account": None}
    account = register(client)
    assert client.get("/api/auth/me").json()["account"] == account
    assert "password" not in account

    assert client.post("/api/auth/register", json={"email": "owner@example.com", "password": "other-password"}).status_code == 409

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").json() == {"account": None}

    assert client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}).status_code == 401
    # Surrounding whitespace was always stripped from passwords.
    response = client.post("/api/auth/login", json={"email": "owner@example.com", "password": f" {PASSWORD} "})
    assert response.status_code == 200
    assert client.get("/api/auth/me").json()["account"]["id"] == account["id"]


def test_session_cookie_is_http_only(client):
    response = client.post("/api/auth/register", json={"email": "a@example.com", "password": PASSWORD})
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_empty_fields_are_rejected(client):
    assert client.post("/api/auth/register", json={"email": "  ", "password": "pw"}).status_code == 422
    register(client)
    assert client.post("/api/groups", json={"name": "   "}).status_code == 422


def test_group_lifecycle_and_ownership(client):
    assert client.post("/api/groups", json={"name": "Demo"}).status_code == 401

    register(client)
    group = create_group(client)
    assert client.post("/api/groups", json={"name": "Demo"}).status_code == 409
    assert [g["name"] for g in client.get("/api/groups/mine").json()] == ["Demo"]

    # Anyone can find a group by name and check saved ids.
    client.post("/api/auth/logout")
    assert client.get("/api/groups/by-name", params={"name": " Demo "}).json()["id"] == group["id"]
    assert client.get("/api/groups/by-name", params={"name": "Nope"}).status_code == 404
    assert client.post("/api/groups/lookup", json={"ids": [group["id"], 999]}).json() == [group]

    # Others can't change it.
    assert client.patch(f"/api/groups/{group['id']}", json={"name": "Hacked"}).status_code == 401
    register(client, email="other@example.com")
    assert client.patch(f"/api/groups/{group['id']}", json={"name": "Hacked"}).status_code == 403
    assert client.delete(f"/api/groups/{group['id']}").status_code == 403

    client.post("/api/auth/login", json={"email": "owner@example.com", "password": PASSWORD})
    assert client.patch(f"/api/groups/{group['id']}", json={"name": "Renamed"}).json()["name"] == "Renamed"
    assert client.delete(f"/api/groups/{group['id']}").status_code == 204
    assert client.get("/api/groups/mine").json() == []


def test_elements(client):
    register(client)
    group = create_group(client)
    assert len(client.get("/api/elements").json()) == 118
    url = f"/api/groups/{group['id']}/elements"
    assert client.put(f"{url}/H").status_code == 204
    assert client.put(f"{url}/H").status_code == 204
    assert client.put(f"{url}/Xx").status_code == 404
    assert client.get(url).json() == ["H"]
    assert client.delete(f"{url}/H").status_code == 204
    assert client.get(url).json() == []


def test_categories_and_compounds(client):
    register(client)
    group = create_group(client)
    gid = group["id"]

    category = client.post(f"/api/groups/{gid}/categories", json={"name": "Acids", "type": "compound"}).json()
    assert category["type"] == "compound"
    assert client.post(f"/api/groups/{gid}/categories", json={"name": "Acids", "type": "compound"}).status_code == 409
    # The same name is fine for the other type.
    question_category = client.post(f"/api/groups/{gid}/categories", json={"name": "Acids", "type": "question"}).json()
    assert [c["id"] for c in client.get(f"/api/groups/{gid}/categories", params={"type": "compound"}).json()] == [category["id"]]

    # A compound can't use a question category.
    assert client.post(f"/api/groups/{gid}/compounds", json={**COMPOUND, "category_id": question_category["id"]}).status_code == 422

    compound = client.post(f"/api/groups/{gid}/compounds", json={**COMPOUND, "category_id": category["id"]})
    assert compound.status_code == 201, compound.text
    compound = compound.json()
    assert compound["wrong_name3"] is None and compound["wrong_name4"] is None

    listed = client.get(f"/api/groups/{gid}/compounds", params={"category_id": category["id"], "difficulty": "easy"}).json()
    assert [c["id"] for c in listed] == [compound["id"]]
    assert client.get(f"/api/groups/{gid}/compounds", params={"difficulty": "hard"}).json() == []

    updated = client.patch(f"/api/compounds/{compound['id']}", json={**COMPOUND, "difficulty": "hard", "category_id": category["id"]})
    assert updated.json()["difficulty"] == "hard"

    renamed = client.patch(f"/api/categories/{category['id']}", json={"name": "Bases"})
    assert renamed.json()["name"] == "Bases"

    # Deleting the category deletes its compounds.
    assert client.delete(f"/api/categories/{category['id']}").status_code == 204
    assert client.get(f"/api/groups/{gid}/compounds").json() == []


def test_questions_need_owner(client):
    register(client)
    gid = create_group(client)["id"]
    category = client.post(f"/api/groups/{gid}/categories", json={"name": "Basics", "type": "question"}).json()
    body = {"question": "What is H?", "correct_answer": "Hydrogen", "wrong_answer1": "Helium",
            "wrong_answer2": "Hafnium", "difficulty": "medium", "category_id": category["id"]}
    question = client.post(f"/api/groups/{gid}/questions", json=body).json()

    client.post("/api/auth/logout")
    assert client.get(f"/api/groups/{gid}/questions").json()[0]["question"] == "What is H?"
    assert client.delete(f"/api/questions/{question['id']}").status_code == 401
    register(client, email="other@example.com")
    assert client.delete(f"/api/questions/{question['id']}").status_code == 403
    assert client.post(f"/api/groups/{gid}/questions", json=body).status_code == 403


def test_frontend_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>FormelX</title>" in response.text


def test_deleting_a_group_deletes_its_content(client):
    register(client)
    gid = create_group(client)["id"]
    client.put(f"/api/groups/{gid}/elements/O")
    category = client.post(f"/api/groups/{gid}/categories", json={"name": "Acids", "type": "compound"}).json()
    client.post(f"/api/groups/{gid}/compounds", json={**COMPOUND, "category_id": category["id"]})

    assert client.delete(f"/api/groups/{gid}").status_code == 204
    assert client.get(f"/api/groups/{gid}/compounds").status_code == 404
    db = client.db
    assert client.portal.call(db.get_entries, "compounds", gid) == []
    assert client.portal.call(db.get_categories, gid) == []
    assert client.portal.call(db.get_group_element_symbols, gid) == []


def test_unique_violations_become_conflicts(client):
    db = client.db
    account = client.portal.call(db.create_account, "a@example.com", "hash")
    client.portal.call(db.create_group, "Same", account["id"])
    with pytest.raises(DatabaseConflictError):
        client.portal.call(db.create_group, "Same", account["id"])
    with pytest.raises(DatabaseConflictError):
        client.portal.call(db.create_account, "a@example.com", "hash")


def test_connection_error_returns_503():
    # Nothing listens on port 1, so connecting fails right away.
    url = "postgresql+asyncpg://formelx:formelx@127.0.0.1:1/formelx"
    settings = Settings(database_url=url, session_secret="test-secret", secure_cookies=False)
    with TestClient(create_app(settings, db=Database(url))) as client:
        response = client.get("/api/elements")
    assert response.status_code == 503
    assert response.json() == {"detail": "connection_error"}


def test_registration_needs_eight_characters(client):
    response = client.post("/api/auth/register", json={"email": "a@example.com", "password": " short7 "})
    assert response.status_code == 422
    assert response.json() == {"detail": "password_too_short"}
    assert client.post("/api/auth/register", json={"email": "a@example.com", "password": "x" * 73}).json() == {"detail": "password_too_long"}
    register(client, email="a@example.com", password="12345678")


def test_old_short_passwords_can_still_log_in(client):
    # Accounts imported from the Android app may have shorter passwords.
    client.portal.call(client.db.create_account, "old@example.com", hash_password("abc"))
    assert client.post("/api/auth/login", json={"email": "old@example.com", "password": "abc"}).status_code == 200


def test_failed_logins_are_rate_limited_per_email(client):
    register(client)
    client.post("/api/auth/logout")
    for _ in range(5):
        assert client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrong"}).status_code == 401
    blocked = client.post("/api/auth/login", json={"email": "owner@example.com", "password": PASSWORD})
    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "too_many_attempts"}
    assert 0 < int(blocked.headers["Retry-After"]) <= 15 * 60
    # Other accounts aren't affected.
    register(client, email="other@example.com")


def test_successful_login_resets_the_email_counter(client):
    register(client)
    for _ in range(4):
        client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrong"})
    assert client.post("/api/auth/login", json={"email": "owner@example.com", "password": PASSWORD}).status_code == 200
    for _ in range(4):
        assert client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrong"}).status_code == 401


def test_registrations_are_rate_limited_per_ip(client):
    for i in range(5):
        register(client, email=f"user{i}@example.com")
    response = client.post("/api/auth/register", json={"email": "user5@example.com", "password": PASSWORD})
    assert response.status_code == 429


def test_rate_limiter_window_expires():
    from src.backend.rate_limit import RateLimiter, Rule

    now = [0.0]
    limiter = RateLimiter(clock=lambda: now[0])
    rule = Rule(limit=2, window=60)
    limiter.hit("k", rule)
    limiter.hit("k", rule)
    assert limiter.retry_after("k", rule) == 60
    now[0] = 30
    assert limiter.retry_after("k", rule) == 30
    now[0] = 60
    assert limiter.retry_after("k", rule) == 0


def test_responses_only_contain_declared_fields(client):
    account = register(client)
    assert set(account) == {"id", "email"}
    gid = create_group(client)["id"]
    category = client.post(f"/api/groups/{gid}/categories", json={"name": "Acids", "type": "compound"}).json()
    assert set(category) == {"id", "name", "type", "group_id"}
    compound = client.post(f"/api/groups/{gid}/compounds", json={**COMPOUND, "category_id": category["id"]}).json()
    assert "date" not in compound
    schema = client.get("/api/openapi.json").json()["components"]["schemas"]
    assert {"AccountOut", "GroupOut", "CategoryOut", "CompoundOut", "QuestionOut", "ElementOut"} <= set(schema)


@pytest.mark.parametrize("email", ["no-at-sign", "two@@example.com", "a@b", "with space@example.com", "a@example."])
def test_registration_rejects_invalid_emails(client, email):
    response = client.post("/api/auth/register", json={"email": email, "password": PASSWORD})
    assert response.status_code == 422
    assert response.json() == {"detail": "invalid_email"}


def test_login_does_not_check_the_email_format(client):
    # Imported accounts may have addresses the new check would reject.
    client.portal.call(client.db.create_account, "legacy-user", hash_password(PASSWORD))
    assert client.post("/api/auth/login", json={"email": "legacy-user", "password": PASSWORD}).status_code == 200
