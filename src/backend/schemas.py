"""Request bodies. Text fields are stripped; empty optional fields become None."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints, field_validator


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


class Credentials(BaseModel):
    email: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=254)]
    # Passwords were always stripped by the app, so keep doing it for existing accounts.
    password: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class GroupIn(BaseModel):
    name: ShortText


class GroupIds(BaseModel):
    ids: list[int]


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
