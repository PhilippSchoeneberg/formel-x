from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..database import Database, DatabaseConflictError
from ..rate_limit import (
    LOGIN_FAILURES_PER_EMAIL, LOGIN_FAILURES_PER_IP, REGISTRATIONS_PER_IP, RateLimiter, client_ip, get_rate_limiter,
)
from ..schemas import MIN_PASSWORD_LENGTH, AccountResponse, Credentials, is_valid_email
from ..security import (
    MAX_PASSWORD_BYTES,
    burn_password_check,
    get_db,
    hash_password,
    login_session,
    logout_session,
    optional_account_id,
    verify_password,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=AccountResponse)
async def me(request: Request, account_id=Depends(optional_account_id), db: Database = Depends(get_db)):
    if account_id is None:
        return {"account": None}
    account = await db.get_account_by_id(account_id)
    if not account:
        logout_session(request)
    return {"account": account}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def register(credentials: Credentials, request: Request, db: Database = Depends(get_db),
                   limiter: RateLimiter = Depends(get_rate_limiter)):
    ip_key = f"register:{client_ip(request)}"
    limiter.check((ip_key, REGISTRATIONS_PER_IP))

    # Only checked when registering, so imported accounts with unusual addresses can still log in.
    if not is_valid_email(credentials.email):
        raise HTTPException(422, "invalid_email")
    if len(credentials.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(422, "password_too_short")
    if len(credentials.password.encode()) > MAX_PASSWORD_BYTES:
        raise HTTPException(422, "password_too_long")
    if await db.get_account_by_email(credentials.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "account_exists")
    try:
        account = await db.create_account(credentials.email, hash_password(credentials.password))
    except DatabaseConflictError:
        raise HTTPException(status.HTTP_409_CONFLICT, "account_exists")

    limiter.hit(ip_key, REGISTRATIONS_PER_IP)
    login_session(request, account["id"])
    return {"account": account}


@router.post("/login", response_model=AccountResponse)
async def login(credentials: Credentials, request: Request, db: Database = Depends(get_db),
                limiter: RateLimiter = Depends(get_rate_limiter)):
    ip_key = f"login-ip:{client_ip(request)}"
    email_key = f"login-email:{credentials.email.lower()}"
    limiter.check((ip_key, LOGIN_FAILURES_PER_IP), (email_key, LOGIN_FAILURES_PER_EMAIL))

    account = await db.get_account_by_email(credentials.email)
    if not account:
        burn_password_check(credentials.password)
    if not account or not verify_password(credentials.password, account["password"]):
        limiter.hit(ip_key, LOGIN_FAILURES_PER_IP)
        limiter.hit(email_key, LOGIN_FAILURES_PER_EMAIL)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid_credentials")

    limiter.reset(email_key)
    login_session(request, account["id"])
    return {"account": account}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request):
    logout_session(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
