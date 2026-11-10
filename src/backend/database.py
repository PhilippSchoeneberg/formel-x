"""Async data access on top of SQLAlchemy Core.

Production uses PostgreSQL (asyncpg); the tests use SQLite in memory (aiosqlite). Every method
returns plain dicts (or lists of dicts) shaped like the table rows, and runs in its own
transaction.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from sqlalchemy import Select, delete, event, func, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

from .tables import ENTRY_TABLES, accounts, categories, elements, elements_to_groups, groups


logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """The database could not be reached (down, network failure, timeout)."""


class DatabaseError(Exception):
    """The database reported an error."""


class DatabaseConflictError(DatabaseError):
    """A unique constraint was violated."""


def create_engine(url):
    if url.startswith("sqlite"):
        engine = create_async_engine(url, poolclass=StaticPool, connect_args={"check_same_thread": False})

        @event.listens_for(engine.sync_engine, "connect")
        def enable_foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")

        return engine
    return create_async_engine(url, pool_pre_ping=True, connect_args={"timeout": 10, "command_timeout": 15})


def _rows(result):
    return [dict(row._mapping) for row in result]


class Database:
    def __init__(self, url, engine=None):
        self.engine = engine or create_engine(url)


    async def close(self):
        await self.engine.dispose()


    @asynccontextmanager
    async def _transaction(self):
        try:
            async with self.engine.begin() as connection:
                yield connection
        except IntegrityError as e:
            if "unique" in str(e.orig).lower() or "duplicate" in str(e.orig).lower():
                raise DatabaseConflictError(str(e.orig)) from e
            logger.error("Integrity error: %s", e)
            raise DatabaseError(str(e.orig)) from e
        except (OperationalError, InterfaceError, OSError, asyncio.TimeoutError) as e:
            logger.error("Database unreachable: %s", e)
            raise DatabaseConnectionError(str(e)) from e
        except DBAPIError as e:
            if e.connection_invalidated:
                raise DatabaseConnectionError(str(e)) from e
            logger.error("Database error: %s", e)
            raise DatabaseError(str(e)) from e
        except SQLAlchemyError as e:
            logger.error("Database error: %s", e)
            raise DatabaseError(str(e)) from e


    async def _all(self, statement):
        async with self._transaction() as connection:
            return _rows(await connection.execute(statement))


    async def _one(self, statement):
        rows = await self._all(statement.limit(1) if isinstance(statement, Select) else statement)
        return rows[0] if rows else None


    async def _execute(self, *statements):
        async with self._transaction() as connection:
            for statement in statements:
                await connection.execute(statement)


    # Accounts

    async def get_account_by_id(self, account_id):
        return await self._one(select(accounts).where(accounts.c.id == account_id))


    async def get_account_by_email(self, email):
        # Case-insensitive, so "Max@example.com" finds the account registered as "max@example.com".
        return await self._one(select(accounts).where(func.lower(accounts.c.email) == email.strip().lower()))


    async def create_account(self, email, password_hash):
        return await self._one(insert(accounts).values(email=email, password=password_hash).returning(*accounts.c))


    # Groups

    async def get_group(self, group_id):
        return await self._one(select(groups).where(groups.c.id == group_id))


    async def get_group_by_name(self, name):
        return await self._one(select(groups).where(groups.c.name == name))


    async def get_groups_by_ids(self, group_ids):
        if not group_ids:
            return []
        return await self._all(select(groups).where(groups.c.id.in_(group_ids)).order_by(groups.c.name))


    async def get_groups_by_owner(self, owner_id):
        return await self._all(select(groups).where(groups.c.owner_id == owner_id).order_by(groups.c.name))


    async def create_group(self, name, owner_id):
        return await self._one(insert(groups).values(name=name, owner_id=owner_id).returning(*groups.c))


    async def update_group(self, group_id, name):
        return await self._one(update(groups).where(groups.c.id == group_id).values(name=name).returning(*groups.c))


    async def delete_group(self, group_id):
        # Foreign keys cascade, but delete explicitly so the order never depends on the database.
        await self._execute(
            delete(elements_to_groups).where(elements_to_groups.c.group_id == group_id),
            *(delete(table).where(table.c.group_id == group_id) for table in ENTRY_TABLES.values()),
            delete(categories).where(categories.c.group_id == group_id),
            delete(groups).where(groups.c.id == group_id),
        )


    # Elements

    async def get_elements(self):
        return await self._all(select(elements).order_by(elements.c.system_period, elements.c.system_group, elements.c.symbol))


    async def get_element(self, symbol):
        return await self._one(select(elements).where(elements.c.symbol == symbol))


    async def get_group_element_symbols(self, group_id):
        rows = await self._all(
            select(elements_to_groups.c.symbol).where(elements_to_groups.c.group_id == group_id).order_by(elements_to_groups.c.symbol)
        )
        return [row["symbol"] for row in rows]


    async def add_element_to_group(self, group_id, symbol):
        try:
            await self._execute(insert(elements_to_groups).values(group_id=group_id, symbol=symbol))
        except DatabaseConflictError:
            pass  # already linked


    async def remove_element_from_group(self, group_id, symbol):
        await self._execute(
            delete(elements_to_groups).where(elements_to_groups.c.group_id == group_id, elements_to_groups.c.symbol == symbol)
        )


    # Categories

    async def get_categories(self, group_id, category_type=None):
        statement = select(categories).where(categories.c.group_id == group_id).order_by(categories.c.name)
        if category_type is not None:
            statement = statement.where(categories.c.type == category_type)
        return await self._all(statement)


    async def get_category(self, category_id):
        return await self._one(select(categories).where(categories.c.id == category_id))


    async def create_category(self, group_id, name, category_type):
        return await self._one(
            insert(categories).values(name=name, type=category_type, group_id=group_id).returning(*categories.c)
        )


    async def update_category(self, category_id, name):
        return await self._one(
            update(categories).where(categories.c.id == category_id).values(name=name).returning(*categories.c)
        )


    async def delete_category(self, category_id):
        await self._execute(
            *(delete(table).where(table.c.category_id == category_id) for table in ENTRY_TABLES.values()),
            delete(categories).where(categories.c.id == category_id),
        )


    # Compounds and questions ("entries")

    async def get_entries(self, table_name, group_id, category_id=None, difficulty=None):
        table = ENTRY_TABLES[table_name]
        statement = select(table).where(table.c.group_id == group_id).order_by(table.c.id)
        if category_id is not None:
            statement = statement.where(table.c.category_id == category_id)
        if difficulty is not None:
            statement = statement.where(table.c.difficulty == difficulty)
        return await self._all(statement)


    async def get_entry(self, table_name, entry_id):
        table = ENTRY_TABLES[table_name]
        return await self._one(select(table).where(table.c.id == entry_id))


    async def create_entry(self, table_name, data):
        table = ENTRY_TABLES[table_name]
        return await self._one(insert(table).values(**data).returning(*table.c))


    async def update_entry(self, table_name, entry_id, data):
        table = ENTRY_TABLES[table_name]
        return await self._one(update(table).where(table.c.id == entry_id).values(**data).returning(*table.c))


    async def delete_entry(self, table_name, entry_id):
        table = ENTRY_TABLES[table_name]
        await self._execute(delete(table).where(table.c.id == entry_id))
