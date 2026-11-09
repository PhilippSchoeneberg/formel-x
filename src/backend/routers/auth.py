from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..database import Database, DatabaseConflictError
from ..schemas import Credentials
from ..security import (
    MAX_PASSWORD_BYTES,
    get_db,
    hash_password,
    login_session,
    logout_session,
    optional_account_id,
    verify_password,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


def public_account(account):
    return {"id": account["id"], "email": account["email"]}


@router.get("/me")
async def me(request: Request, account_id=Depends(optional_account_id), db: Database = Depends(get_db)):
    if account_id is None:
        return {"account": None}
    account = await db.get_account_by_id(account_id)
    if not account:
        logout_session(request)
        return {"account": None}
    return {"account": public_account(account)}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(credentials: Credentials, request: Request, db: Database = Depends(get_db)):
    if len(credentials.password.encode()) > MAX_PASSWORD_BYTES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "password_too_long")
    if await db.get_account_by_email(credentials.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "account_exists")
    try:
        account = await db.create_account(credentials.email, hash_password(credentials.password))
    except DatabaseConflictError:
        raise HTTPException(status.HTTP_409_CONFLICT, "account_exists")
    login_session(request, account["id"])
    return {"account": public_account(account)}


@router.post("/login")
async def login(credentials: Credentials, request: Request, db: Database = Depends(get_db)):
    account = await db.get_account_by_email(credentials.email)
    if not account or not verify_password(credentials.password, account["password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid_credentials")
    login_session(request, account["id"])
    return {"account": public_account(account)}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request):
    logout_session(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
