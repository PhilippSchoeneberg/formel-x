"""Compounds and questions share the same shape: a group, a category, a difficulty and answer options."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..database import Database
from ..schemas import CategoryType, CompoundIn, CompoundOut, Difficulty, QuestionIn, QuestionOut
from ..security import ensure_owner, get_db, get_group_or_404, get_owned_group, require_account_id


def make_router(table, category_type, body_model, response_model):
    router = APIRouter(prefix="/api", tags=[table])

    async def check_category(db, group_id, category_id):
        category = await db.get_category(category_id)
        if not category or category["group_id"] != group_id or category["type"] != category_type.db_value:
            raise HTTPException(422, "invalid_category")

    async def get_owned_entry(entry_id: int, account_id=Depends(require_account_id), db: Database = Depends(get_db)):
        entry = await db.get_entry(table, entry_id)
        if not entry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "entry_not_found")
        ensure_owner(await db.get_group(entry["group_id"]), account_id)
        return entry

    @router.get(f"/groups/{{group_id}}/{table}", response_model=list[response_model])
    async def list_entries(category_id: int | None = None, difficulty: Difficulty | None = None,
                           group=Depends(get_group_or_404), db: Database = Depends(get_db)):
        return await db.get_entries(table, group["id"], category_id, difficulty)

    @router.post(f"/groups/{{group_id}}/{table}", status_code=status.HTTP_201_CREATED, response_model=response_model)
    async def create_entry(body: body_model, group=Depends(get_owned_group), db: Database = Depends(get_db)):
        await check_category(db, group["id"], body.category_id)
        return await db.create_entry(table, {**body.model_dump(), "group_id": group["id"]})

    @router.patch(f"/{table}/{{entry_id}}", response_model=response_model)
    async def update_entry(body: body_model, entry=Depends(get_owned_entry), db: Database = Depends(get_db)):
        await check_category(db, entry["group_id"], body.category_id)
        return await db.update_entry(table, entry["id"], body.model_dump())

    @router.delete(f"/{table}/{{entry_id}}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_entry(entry=Depends(get_owned_entry), db: Database = Depends(get_db)):
        await db.delete_entry(table, entry["id"])
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


compounds_router = make_router("compounds", CategoryType.compound, CompoundIn, CompoundOut)
questions_router = make_router("questions", CategoryType.question, QuestionIn, QuestionOut)
