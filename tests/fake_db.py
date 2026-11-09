"""In-memory stand-in for `src.backend.database.Database`, used by the tests and for offline UI checks."""

import itertools

from src.backend.database import ENTRY_TABLES, DatabaseConflictError


SAMPLE_ELEMENTS = [
    {"symbol": "H", "name": "hydrogen", "system_group": 1, "system_period": 1},
    {"symbol": "He", "name": "helium", "system_group": 18, "system_period": 1},
    {"symbol": "Li", "name": "lithium", "system_group": 1, "system_period": 2},
    {"symbol": "C", "name": "carbon", "system_group": 14, "system_period": 2},
    {"symbol": "O", "name": "oxygen", "system_group": 16, "system_period": 2},
    {"symbol": "Na", "name": "sodium", "system_group": 1, "system_period": 3},
]


class FakeDatabase:
    def __init__(self, elements=None):
        self._ids = itertools.count(1)
        self.tables = {name: [] for name in ("accounts", "groups", "elements_to_groups", "categories", *ENTRY_TABLES)}
        self.elements = list(elements or SAMPLE_ELEMENTS)

    def _insert(self, table, row):
        row = {"id": next(self._ids), **row}
        self.tables[table].append(row)
        return dict(row)

    def _find(self, table, **filters):
        return [dict(row) for row in self.tables[table] if all(row.get(k) == v for k, v in filters.items())]

    def _first(self, table, **filters):
        rows = self._find(table, **filters)
        return rows[0] if rows else None

    def _update(self, table, row_id, data):
        for row in self.tables[table]:
            if row["id"] == row_id:
                row.update(data)
                return dict(row)

    def _delete(self, table, **filters):
        self.tables[table] = [row for row in self.tables[table] if not all(row.get(k) == v for k, v in filters.items())]

    async def close(self):
        pass

    async def get_account_by_id(self, account_id):
        return self._first("accounts", id=account_id)

    async def get_account_by_email(self, email):
        return self._first("accounts", email=email)

    async def create_account(self, email, password_hash):
        if self._first("accounts", email=email):
            raise DatabaseConflictError("duplicate email")
        return self._insert("accounts", {"email": email, "password": password_hash})

    async def get_group(self, group_id):
        return self._first("groups", id=group_id)

    async def get_group_by_name(self, name):
        return self._first("groups", name=name)

    async def get_groups_by_ids(self, group_ids):
        return sorted((g for g in self._find("groups") if g["id"] in group_ids), key=lambda g: g["name"])

    async def get_groups_by_owner(self, owner_id):
        return sorted(self._find("groups", owner_id=owner_id), key=lambda g: g["name"])

    async def create_group(self, name, owner_id):
        if self._first("groups", name=name):
            raise DatabaseConflictError("duplicate group")
        return self._insert("groups", {"name": name, "owner_id": owner_id})

    async def update_group(self, group_id, name):
        return self._update("groups", group_id, {"name": name})

    async def delete_group(self, group_id):
        for table in ("elements_to_groups", *ENTRY_TABLES, "categories"):
            self._delete(table, group_id=group_id)
        self._delete("groups", id=group_id)

    async def get_elements(self):
        return [dict(element) for element in self.elements]

    async def get_element(self, symbol):
        return next((dict(e) for e in self.elements if e["symbol"] == symbol), None)

    async def get_group_element_symbols(self, group_id):
        return [row["symbol"] for row in self._find("elements_to_groups", group_id=group_id)]

    async def add_element_to_group(self, group_id, symbol):
        if not self._first("elements_to_groups", group_id=group_id, symbol=symbol):
            self.tables["elements_to_groups"].append({"group_id": group_id, "symbol": symbol})

    async def remove_element_from_group(self, group_id, symbol):
        self._delete("elements_to_groups", group_id=group_id, symbol=symbol)

    async def get_categories(self, group_id, category_type=None):
        filters = {"group_id": group_id}
        if category_type is not None:
            filters["type"] = category_type
        return sorted(self._find("categories", **filters), key=lambda c: c["name"])

    async def get_category(self, category_id):
        return self._first("categories", id=category_id)

    async def create_category(self, group_id, name, category_type):
        return self._insert("categories", {"name": name, "type": category_type, "group_id": group_id})

    async def update_category(self, category_id, name):
        return self._update("categories", category_id, {"name": name})

    async def delete_category(self, category_id):
        for table in ENTRY_TABLES:
            self._delete(table, category_id=category_id)
        self._delete("categories", id=category_id)

    async def get_entries(self, table, group_id, category_id=None, difficulty=None):
        filters = {"group_id": group_id}
        if category_id is not None:
            filters["category_id"] = category_id
        if difficulty is not None:
            filters["difficulty"] = difficulty
        return self._find(table, **filters)

    async def get_entry(self, table, entry_id):
        return self._first(table, id=entry_id)

    async def create_entry(self, table, data):
        return self._insert(table, dict(data))

    async def update_entry(self, table, entry_id, data):
        return self._update(table, entry_id, dict(data))

    async def delete_entry(self, table, entry_id):
        self._delete(table, id=entry_id)
