from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..database import Database
from ..schemas import CategoryIn, CategoryType, CategoryUpdate
from ..security import ensure_owner, get_db, get_group_or_404, get_owned_group, require_account_id


router = APIRouter(prefix="/api", tags=["categories"])


def public_category(category):
    return {
        "id": category["id"],
        "name": category["name"],
        "type": CategoryType.from_db(category["type"]).value,
        "group_id": category["group_id"],
    }


async def _name_taken(db, group_id, category_type, name, exclude_id=None):
    for category in await db.get_categories(group_id, category_type.db_value):
        if category["name"] == name and category["id"] != exclude_id:
            return True
    return False


async def get_owned_category(category_id: int, account_id=Depends(require_account_id), db: Database = Depends(get_db)):
    category = await db.get_category(category_id)
    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "category_not_found")
    ensure_owner(await db.get_group(category["group_id"]), account_id)
    return category


@router.get("/groups/{group_id}/categories")
async def list_categories(type: CategoryType | None = None, group=Depends(get_group_or_404), db: Database = Depends(get_db)):
    categories = await db.get_categories(group["id"], type.db_value if type else None)
    return [public_category(category) for category in categories]


@router.post("/groups/{group_id}/categories", status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryIn, group=Depends(get_owned_group), db: Database = Depends(get_db)):
    if await _name_taken(db, group["id"], body.type, body.name):
        raise HTTPException(status.HTTP_409_CONFLICT, "category_exists")
    return public_category(await db.create_category(group["id"], body.name, body.type.db_value))


@router.patch("/categories/{category_id}")
async def update_category(body: CategoryUpdate, category=Depends(get_owned_category), db: Database = Depends(get_db)):
    category_type = CategoryType.from_db(category["type"])
    if await _name_taken(db, category["group_id"], category_type, body.name, exclude_id=category["id"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "category_exists")
    return public_category(await db.update_category(category["id"], body.name))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category=Depends(get_owned_category), db: Database = Depends(get_db)):
    await db.delete_category(category["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
