"""Create the initial schema and add the elements.

Revision ID: 0001
Revises:
Create Date: 2026-11-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.backend.elements_data import ELEMENTS


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

Id = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def created():
    return sa.Column("date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", Id, nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        created(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
        sa.UniqueConstraint("email", name=op.f("uq_accounts_email")),
    )
    elements = op.create_table(
        "elements",
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("system_group", sa.Integer(), nullable=False),
        sa.Column("system_period", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("symbol", name=op.f("pk_elements")),
    )
    op.create_table(
        "groups",
        sa.Column("id", Id, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("owner_id", Id, nullable=False),
        created(),
        sa.ForeignKeyConstraint(["owner_id"], ["accounts.id"], name=op.f("fk_groups_owner_id_accounts"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
        sa.UniqueConstraint("name", name=op.f("uq_groups_name")),
    )
    op.create_index(op.f("ix_groups_owner_id"), "groups", ["owner_id"])
    op.create_table(
        "categories",
        sa.Column("id", Id, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.Integer(), nullable=False),
        sa.Column("group_id", Id, nullable=False),
        created(),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name=op.f("fk_categories_group_id_groups"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
    )
    op.create_index(op.f("ix_categories_group_id"), "categories", ["group_id"])
    op.create_table(
        "elements_to_groups",
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("group_id", Id, nullable=False),
        created(),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name=op.f("fk_elements_to_groups_group_id_groups"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["symbol"], ["elements.symbol"], name=op.f("fk_elements_to_groups_symbol_elements"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("symbol", "group_id", name=op.f("pk_elements_to_groups")),
    )
    op.create_index(op.f("ix_elements_to_groups_group_id"), "elements_to_groups", ["group_id"])
    op.create_table(
        "compounds",
        sa.Column("id", Id, nullable=False),
        sa.Column("correct_name", sa.Text(), nullable=False),
        sa.Column("wrong_name1", sa.Text(), nullable=False),
        sa.Column("wrong_name2", sa.Text(), nullable=False),
        sa.Column("wrong_name3", sa.Text(), nullable=True),
        sa.Column("wrong_name4", sa.Text(), nullable=True),
        sa.Column("correct_formula", sa.Text(), nullable=False),
        sa.Column("wrong_formula1", sa.Text(), nullable=False),
        sa.Column("wrong_formula2", sa.Text(), nullable=False),
        sa.Column("wrong_formula3", sa.Text(), nullable=True),
        sa.Column("wrong_formula4", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Text(), nullable=False),
        sa.Column("category_id", Id, nullable=False),
        sa.Column("group_id", Id, nullable=False),
        created(),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name=op.f("fk_compounds_category_id_categories"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name=op.f("fk_compounds_group_id_groups"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_compounds")),
    )
    op.create_index(op.f("ix_compounds_category_id"), "compounds", ["category_id"])
    op.create_index(op.f("ix_compounds_group_id"), "compounds", ["group_id"])
    op.create_table(
        "questions",
        sa.Column("id", Id, nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("wrong_answer1", sa.Text(), nullable=False),
        sa.Column("wrong_answer2", sa.Text(), nullable=False),
        sa.Column("wrong_answer3", sa.Text(), nullable=True),
        sa.Column("wrong_answer4", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Text(), nullable=False),
        sa.Column("category_id", Id, nullable=False),
        sa.Column("group_id", Id, nullable=False),
        created(),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name=op.f("fk_questions_category_id_categories"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name=op.f("fk_questions_group_id_groups"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_questions")),
    )
    op.create_index(op.f("ix_questions_category_id"), "questions", ["category_id"])
    op.create_index(op.f("ix_questions_group_id"), "questions", ["group_id"])

    op.bulk_insert(elements, [
        {"symbol": symbol, "name": name, "system_group": group, "system_period": period}
        for symbol, name, group, period in ELEMENTS
    ])


def downgrade() -> None:
    for table in ("questions", "compounds", "elements_to_groups", "categories", "groups", "elements", "accounts"):
        op.drop_table(table)
