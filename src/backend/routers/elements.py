from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..database import Database
from ..security import get_db, get_group_or_404, get_owned_group


router = APIRouter(prefix="/api", tags=["elements"])


@router.get("/elements")
async def all_elements(response: Response, db: Database = Depends(get_db)):
    # The periodic table doesn't change, so let browsers cache it for a day.
    response.headers["Cache-Control"] = "public, max-age=86400"
    return await db.get_elements()


@router.get("/groups/{group_id}/elements")
async def group_elements(group=Depends(get_group_or_404), db: Database = Depends(get_db)):
    return await db.get_group_element_symbols(group["id"])


async def _existing_element(symbol: str, db: Database = Depends(get_db)):
    element = await db.get_element(symbol)
    if not element:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "element_not_found")
    return element


@router.put("/groups/{group_id}/elements/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def add_element(group=Depends(get_owned_group), element=Depends(_existing_element), db: Database = Depends(get_db)):
    await db.add_element_to_group(group["id"], element["symbol"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/groups/{group_id}/elements/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_element(symbol: str, group=Depends(get_owned_group), db: Database = Depends(get_db)):
    await db.remove_element_from_group(group["id"], symbol)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
