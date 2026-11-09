"""Thin async wrapper around Supabase's PostgREST API.

Only the backend talks to Supabase, using a server-side key from the environment.
Every method returns plain dicts (or lists of dicts) shaped like the table rows.
"""

import logging

import httpx


logger = logging.getLogger(__name__)

ENTRY_TABLES = ("compounds", "questions")


class DatabaseConnectionError(Exception):
    """The database could not be reached (offline, DNS failure, timeout)."""


class DatabaseError(Exception):
    """The database answered with an error status."""


class DatabaseConflictError(DatabaseError):
    """A unique constraint was violated (HTTP 409 from PostgREST)."""


class Database:
    def __init__(self, url, key, transport=None):
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        self.client = httpx.AsyncClient(
            base_url=f"{url}/rest/v1",
            headers=headers,
            timeout=10,
            transport=transport,
        )


    async def close(self):
        await self.client.aclose()


    async def _request(self, method, path, params=None, json=None):
        try:
            response = await self.client.request(method, path, params=params, json=json)
        except httpx.TransportError as e:
            raise DatabaseConnectionError(str(e)) from e
        if response.status_code == 409:
            raise DatabaseConflictError(response.text)
        if response.is_error:
            logger.error("Supabase %s %s failed with %s: %s", method, path, response.status_code, response.text)
            raise DatabaseError(f"{response.status_code}")
        if not response.content:
            return None
        return response.json()


    async def _get_one(self, table, params):
        rows = await self._request("GET", f"/{table}", params={**params, "limit": 1})
        return rows[0] if rows else None


    # Accounts

    async def get_account_by_id(self, account_id):
        return await self._get_one("accounts", {"id": f"eq.{account_id}"})


    async def get_account_by_email(self, email):
        return await self._get_one("accounts", {"email": f"eq.{email}"})


    async def create_account(self, email, password_hash):
        rows = await self._request("POST", "/accounts", json={"email": email, "password": password_hash})
        return rows[0]


    # Groups

    async def get_group(self, group_id):
        return await self._get_one("groups", {"id": f"eq.{group_id}"})


    async def get_group_by_name(self, name):
        return await self._get_one("groups", {"name": f"eq.{name}"})


    async def get_groups_by_ids(self, group_ids):
        if not group_ids:
            return []
        ids = ",".join(str(int(group_id)) for group_id in group_ids)
        return await self._request("GET", "/groups", params={"id": f"in.({ids})", "order": "name.asc"})


    async def get_groups_by_owner(self, owner_id):
        return await self._request("GET", "/groups", params={"owner_id": f"eq.{owner_id}", "order": "name.asc"})


    async def create_group(self, name, owner_id):
        rows = await self._request("POST", "/groups", json={"name": name, "owner_id": owner_id})
        return rows[0]


    async def update_group(self, group_id, name):
        rows = await self._request("PATCH", "/groups", params={"id": f"eq.{group_id}"}, json={"name": name})
        return rows[0]


    async def delete_group(self, group_id):
        # The schema cascades, but delete the content explicitly in case an older database lacks the cascades.
        for table in ("elements_to_groups", *ENTRY_TABLES, "categories"):
            await self._request("DELETE", f"/{table}", params={"group_id": f"eq.{group_id}"})
        await self._request("DELETE", "/groups", params={"id": f"eq.{group_id}"})


    # Elements

    async def get_elements(self):
        return await self._request("GET", "/elements")


    async def get_element(self, symbol):
        return await self._get_one("elements", {"symbol": f"eq.{symbol}"})


    async def get_group_element_symbols(self, group_id):
        rows = await self._request("GET", "/elements_to_groups", params={"group_id": f"eq.{group_id}", "select": "symbol"})
        return [row["symbol"] for row in rows]


    async def add_element_to_group(self, group_id, symbol):
        # Ignore the request if the element is already linked.
        if symbol in await self.get_group_element_symbols(group_id):
            return
        await self._request("POST", "/elements_to_groups", json={"symbol": symbol, "group_id": group_id})


    async def remove_element_from_group(self, group_id, symbol):
        await self._request("DELETE", "/elements_to_groups", params={"group_id": f"eq.{group_id}", "symbol": f"eq.{symbol}"})


    # Categories

    async def get_categories(self, group_id, category_type=None):
        params = {"group_id": f"eq.{group_id}", "order": "name.asc"}
        if category_type is not None:
            params["type"] = f"eq.{category_type}"
        return await self._request("GET", "/categories", params=params)


    async def get_category(self, category_id):
        return await self._get_one("categories", {"id": f"eq.{category_id}"})


    async def create_category(self, group_id, name, category_type):
        rows = await self._request("POST", "/categories", json={"name": name, "type": category_type, "group_id": group_id})
        return rows[0]


    async def update_category(self, category_id, name):
        rows = await self._request("PATCH", "/categories", params={"id": f"eq.{category_id}"}, json={"name": name})
        return rows[0]


    async def delete_category(self, category_id):
        for table in ENTRY_TABLES:
            await self._request("DELETE", f"/{table}", params={"category_id": f"eq.{category_id}"})
        await self._request("DELETE", "/categories", params={"id": f"eq.{category_id}"})


    # Compounds and questions ("entries")

    async def get_entries(self, table, group_id, category_id=None, difficulty=None):
        params = {"group_id": f"eq.{group_id}", "order": "id.asc"}
        if category_id is not None:
            params["category_id"] = f"eq.{category_id}"
        if difficulty is not None:
            params["difficulty"] = f"eq.{difficulty}"
        return await self._request("GET", f"/{table}", params=params)


    async def get_entry(self, table, entry_id):
        return await self._get_one(table, {"id": f"eq.{entry_id}"})


    async def create_entry(self, table, data):
        rows = await self._request("POST", f"/{table}", json=data)
        return rows[0]


    async def update_entry(self, table, entry_id, data):
        rows = await self._request("PATCH", f"/{table}", params={"id": f"eq.{entry_id}"}, json=data)
        return rows[0]


    async def delete_entry(self, table, entry_id):
        await self._request("DELETE", f"/{table}", params={"id": f"eq.{entry_id}"})
