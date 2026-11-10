"""Password hashing and session-based access checks."""

import bcrypt
from fastapi import Depends, HTTPException, Request, status

from .database import Database


# bcrypt only looks at the first 72 bytes of a password and refuses longer input.
MAX_PASSWORD_BYTES = 72


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


_dummy_hash = None


def burn_password_check(password):
    """Spends the same time as a real check, for logins with an unknown email address.

    Without it, "no such account" answers faster than "wrong password", and the response time
    reveals which email addresses have an account.
    """
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = hash_password("formelx-timing-equalizer")
    verify_password(password, _dummy_hash)


def get_db(request: Request) -> Database:
    return request.app.state.db


def login_session(request: Request, account_id: int):
    request.session.clear()
    request.session["account_id"] = account_id


def logout_session(request: Request):
    request.session.clear()


def optional_account_id(request: Request):
    return request.session.get("account_id")


def require_account_id(account_id=Depends(optional_account_id)):
    if account_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not_logged_in")
    return account_id


async def get_group_or_404(group_id: int, db: Database = Depends(get_db)):
    group = await db.get_group(group_id)
    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "group_not_found")
    return group


def ensure_owner(group, account_id):
    if group["owner_id"] != account_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not_group_owner")


async def get_owned_group(group=Depends(get_group_or_404), account_id=Depends(require_account_id)):
    ensure_owner(group, account_id)
    return group
