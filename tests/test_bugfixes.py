"""Regression tests for bugs found in the November 2026 bug sweep."""

from tests.test_api import COMPOUND, PASSWORD, create_group, register


def _compound_category(client):
    register(client)
    gid = create_group(client)["id"]
    category = client.post(f"/api/groups/{gid}/categories", json={"name": "Acids", "type": "compound"}).json()
    return gid, category["id"]


def test_duplicate_compound_answers_are_rejected(client):
    gid, cid = _compound_category(client)
    url = f"/api/groups/{gid}/compounds"
    # A wrong name equal to the correct one (ignoring case and spaces) …
    same_name = {**COMPOUND, "wrong_name2": " water ", "category_id": cid}
    assert client.post(url, json=same_name).json() == {"detail": "duplicate_answers"}
    # … or the same formula written with braces.
    same_formula = {**COMPOUND, "wrong_formula1": "H_{2}O", "category_id": cid}
    assert client.post(url, json=same_formula).status_code == 422
    # Formulas are case-sensitive: CO (carbon monoxide) and Co (cobalt) are different.
    co = {**COMPOUND, "correct_formula": "CO", "wrong_formula1": "Co", "wrong_formula2": "CO_2", "category_id": cid}
    assert client.post(url, json=co).status_code == 201

    entry = client.post(url, json={**COMPOUND, "category_id": cid}).json()
    assert client.patch(f"/api/compounds/{entry['id']}", json=same_name).status_code == 422


def test_duplicate_question_answers_are_rejected(client):
    register(client)
    gid = create_group(client)["id"]
    cid = client.post(f"/api/groups/{gid}/categories", json={"name": "Basics", "type": "question"}).json()["id"]
    body = {"question": "What is H?", "correct_answer": "Hydrogen", "wrong_answer1": "Helium",
            "wrong_answer2": "Hafnium", "wrong_answer3": "HYDROGEN", "difficulty": "easy", "category_id": cid}
    assert client.post(f"/api/groups/{gid}/questions", json=body).json() == {"detail": "duplicate_answers"}


def test_email_addresses_are_case_insensitive(client):
    account = register(client, email="Max.Muster@Example.com")
    assert account["email"] == "max.muster@example.com"
    client.post("/api/auth/logout")

    login = client.post("/api/auth/login", json={"email": "MAX.MUSTER@example.COM", "password": PASSWORD})
    assert login.status_code == 200
    client.post("/api/auth/logout")

    again = client.post("/api/auth/register", json={"email": "max.muster@EXAMPLE.com", "password": PASSWORD})
    assert again.status_code == 409


def test_old_mixed_case_emails_still_log_in(client):
    # Accounts imported with capitals in the stored address.
    from src.backend.security import hash_password

    client.portal.call(client.db.create_account, "Old.User@Example.com", hash_password(PASSWORD))
    assert client.post("/api/auth/login", json={"email": "old.user@example.com", "password": PASSWORD}).status_code == 200


def test_writes_behind_a_proxy_that_rewrites_host(client):
    # nginx's default proxy_set_header Host is the upstream address; the browser's Origin is the
    # public one, which arrives in X-Forwarded-Host.
    headers = {"Origin": "https://formelx.example", "Host": "127.0.0.1:8000", "X-Forwarded-Host": "formelx.example"}
    response = client.post("/api/auth/register", json={"email": "a@example.com", "password": PASSWORD}, headers=headers)
    assert response.status_code == 201

    other = {**headers, "Origin": "https://evil.example"}
    assert client.post("/api/auth/logout", headers=other).status_code == 403


def test_updating_something_deleted_meanwhile_returns_404(client, monkeypatch):
    register(client)
    gid = create_group(client)["id"]

    async def vanished(*args, **kwargs):
        return None

    monkeypatch.setattr(client.db, "update_group", vanished)
    response = client.patch(f"/api/groups/{gid}", json={"name": "Renamed"})
    assert response.status_code == 404
