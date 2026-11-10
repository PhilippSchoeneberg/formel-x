"""Request and response models.

Request bodies strip text; empty optional fields become None. Response models list exactly the
fields the API returns: anything else in a database row (password hashes, dates) is dropped.
"""

import re
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator


ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Difficulty = Literal["easy", "medium", "hard"]


class CategoryType(str, Enum):
    compound = "compound"
    question = "question"

    @property
    def db_value(self):
        # Stored as an integer in the database: compound = 0, question = 1.
        return 0 if self is CategoryType.compound else 1

    @classmethod
    def from_db(cls, value):
        return cls.compound if value == 0 else cls.question


def _empty_to_none(value):
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


# Registration needs at least this many characters (after stripping). Login doesn't check it,
# so older accounts with shorter passwords can still log in.
MIN_PASSWORD_LENGTH = 8

# A deliberately simple check for new accounts: one @, no spaces, and a dot in the domain.
# Must match EMAIL_PATTERN in src/frontend/js/dialogs.js.
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(email):
    return bool(EMAIL_PATTERN.fullmatch(email))


class Credentials(BaseModel):
    email: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=254)]
    # Passwords were always stripped by the app, so keep doing it for existing accounts.
    password: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1024)]


class GroupIn(BaseModel):
    name: ShortText


class GroupIds(BaseModel):
    ids: list[int] = Field(max_length=100)


class CategoryIn(BaseModel):
    name: ShortText
    type: CategoryType


class CategoryUpdate(BaseModel):
    name: ShortText


class CompoundIn(BaseModel):
    correct_name: ShortText
    wrong_name1: ShortText
    wrong_name2: ShortText
    wrong_name3: ShortText | None = None
    wrong_name4: ShortText | None = None
    correct_formula: ShortText
    wrong_formula1: ShortText
    wrong_formula2: ShortText
    wrong_formula3: ShortText | None = None
    wrong_formula4: ShortText | None = None
    difficulty: Difficulty
    category_id: int

    _optional = field_validator("wrong_name3", "wrong_name4", "wrong_formula3", "wrong_formula4", mode="before")(_empty_to_none)


class QuestionIn(BaseModel):
    question: LongText
    correct_answer: ShortText
    wrong_answer1: ShortText
    wrong_answer2: ShortText
    wrong_answer3: ShortText | None = None
    wrong_answer4: ShortText | None = None
    difficulty: Difficulty
    category_id: int

    _optional = field_validator("wrong_answer3", "wrong_answer4", mode="before")(_empty_to_none)


# Responses -------------------------------------------------------------------


class AccountOut(BaseModel):
    id: int
    email: str


class AccountResponse(BaseModel):
    account: AccountOut | None


class GroupOut(BaseModel):
    id: int
    name: str
    owner_id: int


class ElementOut(BaseModel):
    symbol: str
    name: str
    system_group: int
    system_period: int


class CategoryOut(BaseModel):
    id: int
    name: str
    type: CategoryType
    group_id: int

    @field_validator("type", mode="before")
    @classmethod
    def _from_db(cls, value):
        return CategoryType.from_db(value) if isinstance(value, int) else value


class CompoundOut(BaseModel):
    id: int
    correct_name: str
    wrong_name1: str
    wrong_name2: str
    wrong_name3: str | None
    wrong_name4: str | None
    correct_formula: str
    wrong_formula1: str
    wrong_formula2: str
    wrong_formula3: str | None
    wrong_formula4: str | None
    difficulty: Difficulty
    category_id: int
    group_id: int


class QuestionOut(BaseModel):
    id: int
    question: str
    correct_answer: str
    wrong_answer1: str
    wrong_answer2: str
    wrong_answer3: str | None
    wrong_answer4: str | None
    difficulty: Difficulty
    category_id: int
    group_id: int
