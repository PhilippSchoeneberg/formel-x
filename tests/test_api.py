import httpx
import pytest
from fastapi.testclient import TestClient

from src.backend.app import create_app
from src.backend.config import Settings
from src.backend.database import Database
from src.backend.security import hash_password, verify_password
from tests.fake_db import FakeDatabase


SETTINGS = Settings(supabase_url="http://unused", supabase_key="unused", session_secret="test-secret", secure_cookies=False)

COMPOUND = {
    "correct_name": "Water", "wrong_name1": "Hydrogen peroxide", "wrong_name2": "Oxygen",
    "wrong_name3": "", "wrong_name4": None,
    "correct_formula": "H_2O", "wrong_formula1": "H_2O_2", "wrong_formula2": "O_2",
    "difficulty": "easy",
}


@pytest.fixture
def db():
    return FakeDatabase()


@pytest.fixture
def client(db):
    with TestClient(create_app(SETTINGS, db=db)) as client:
        yield client


def register(client, email="owner@example.com", password="secret"):
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

    assert client.post("/api/auth/register", json={"email": "owner@example.com", "password": "other"}).status_code == 409

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").json() == {"account": None}

    assert client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "secret"}).status_code == 401
    # Surrounding whitespace was always stripped from passwords.
    response = client.post("/api/auth/login", json={"email": "owner@example.com", "password": " secret "})
    assert response.status_code == 200
    assert client.get("/api/auth/me").json()["account"]["id"] == account["id"]


def test_session_cookie_is_http_only(client):
    response = client.post("/api/auth/register", json={"email": "a@example.com", "password": "pw"})
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

    client.post("/api/auth/login", json={"email": "owner@example.com", "password": "secret"})
    assert client.patch(f"/api/groups/{group['id']}", json={"name": "Renamed"}).json()["name"] == "Renamed"
    assert client.delete(f"/api/groups/{group['id']}").status_code == 204
    assert client.get("/api/groups/mine").json() == []


def test_elements(client):
    register(client)
    group = create_group(client)
    assert len(client.get("/api/elements").json()) == 6
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


def test_connection_error_returns_503():
    def fail(request):
        raise httpx.ConnectError("offline")

    db = Database("http://supabase.invalid", "key", transport=httpx.MockTransport(fail))
    with TestClient(create_app(SETTINGS, db=db)) as client:
        response = client.get("/api/elements")
    assert response.status_code == 503
    assert response.json() == {"detail": "connection_error"}
