from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..database import Database, DatabaseConflictError
from ..schemas import GroupIds, GroupIn, GroupOut
from ..security import get_db, get_owned_group, require_account_id


router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("/mine", response_model=list[GroupOut])
async def my_groups(account_id=Depends(require_account_id), db: Database = Depends(get_db)):
    return await db.get_groups_by_owner(account_id)


@router.get("/by-name", response_model=GroupOut)
async def group_by_name(name: str, db: Database = Depends(get_db)):
    group = await db.get_group_by_name(name.strip())
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "group_not_found")
    return group


@router.post("/lookup", response_model=list[GroupOut])
async def lookup_groups(body: GroupIds, db: Database = Depends(get_db)):
    """Returns the groups that still exist out of the given ids (used for groups saved in the browser)."""
    return await db.get_groups_by_ids(body.ids[:100])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupOut)
async def create_group(body: GroupIn, account_id=Depends(require_account_id), db: Database = Depends(get_db)):
    if await db.get_group_by_name(body.name):
        raise HTTPException(status.HTTP_409_CONFLICT, "group_exists")
    try:
        return await db.create_group(body.name, account_id)
    except DatabaseConflictError:
        raise HTTPException(status.HTTP_409_CONFLICT, "group_exists")


@router.patch("/{group_id}", response_model=GroupOut)
async def update_group(body: GroupIn, group=Depends(get_owned_group), db: Database = Depends(get_db)):
    existing = await db.get_group_by_name(body.name)
    if existing and existing["id"] != group["id"]:
        raise HTTPException(status.HTTP_409_CONFLICT, "group_exists")
    try:
        return await db.update_group(group["id"], body.name)
    except DatabaseConflictError:
        raise HTTPException(status.HTTP_409_CONFLICT, "group_exists")


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group=Depends(get_owned_group), db: Database = Depends(get_db)):
    await db.delete_group(group["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
