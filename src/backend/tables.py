"""Database schema (SQLAlchemy Core). Alembic migrations in src/backend/migrations create it.

Column names match the original Supabase schema, so data can be imported one to one.
"""

from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, Integer, MetaData, PrimaryKeyConstraint, Table, Text, func,
)


# SQLite (used by the tests) only auto-increments INTEGER primary keys.
Id = BigInteger().with_variant(Integer(), "sqlite")

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})


def _created():
    return Column("date", DateTime(), nullable=False, server_default=func.now())


def _group_id():
    return Column("group_id", Id, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)


def _category_id():
    return Column("category_id", Id, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)


accounts = Table(
    "accounts", metadata,
    Column("id", Id, primary_key=True),
    Column("email", Text, nullable=False, unique=True),
    Column("password", Text, nullable=False),
    _created(),
)

groups = Table(
    "groups", metadata,
    Column("id", Id, primary_key=True),
    Column("name", Text, nullable=False, unique=True),
    Column("owner_id", Id, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True),
    _created(),
)

elements = Table(
    "elements", metadata,
    Column("symbol", Text, primary_key=True),
    Column("name", Text, nullable=False),
    Column("system_group", Integer, nullable=False),
    Column("system_period", Integer, nullable=False),
)

elements_to_groups = Table(
    "elements_to_groups", metadata,
    Column("symbol", Text, ForeignKey("elements.symbol", ondelete="CASCADE"), nullable=False),
    _group_id(),
    _created(),
    PrimaryKeyConstraint("symbol", "group_id"),
)

categories = Table(
    "categories", metadata,
    Column("id", Id, primary_key=True),
    Column("name", Text, nullable=False),
    Column("type", Integer, nullable=False),  # compound = 0, question = 1
    _group_id(),
    _created(),
)

compounds = Table(
    "compounds", metadata,
    Column("id", Id, primary_key=True),
    Column("correct_name", Text, nullable=False),
    Column("wrong_name1", Text, nullable=False),
    Column("wrong_name2", Text, nullable=False),
    Column("wrong_name3", Text),
    Column("wrong_name4", Text),
    Column("correct_formula", Text, nullable=False),
    Column("wrong_formula1", Text, nullable=False),
    Column("wrong_formula2", Text, nullable=False),
    Column("wrong_formula3", Text),
    Column("wrong_formula4", Text),
    Column("difficulty", Text, nullable=False),
    _category_id(),
    _group_id(),
    _created(),
)

questions = Table(
    "questions", metadata,
    Column("id", Id, primary_key=True),
    Column("question", Text, nullable=False),
    Column("correct_answer", Text, nullable=False),
    Column("wrong_answer1", Text, nullable=False),
    Column("wrong_answer2", Text, nullable=False),
    Column("wrong_answer3", Text),
    Column("wrong_answer4", Text),
    Column("difficulty", Text, nullable=False),
    _category_id(),
    _group_id(),
    _created(),
)

ENTRY_TABLES = {"compounds": compounds, "questions": questions}
