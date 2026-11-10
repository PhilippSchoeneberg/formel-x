from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import FRONTEND_DIR, Settings
from .database import Database, DatabaseConnectionError, DatabaseError
from .middleware import BodySizeLimitMiddleware, SameOriginMiddleware, SecurityHeadersMiddleware
from .rate_limit import RateLimiter
from .routers import auth, categories, elements, entries, groups


SESSION_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


class FrontendFiles(StaticFiles):
    """Static files that browsers re-validate on every load (cheap 304s thanks to the ETag).

    Without a Cache-Control header, browsers guess how long to cache and can keep running old
    JavaScript modules after a deploy, mixed with new ones.
    """

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response


def create_app(settings: Settings, db=None):
    """Builds the app. Tests pass their own `db`; otherwise settings.database_url is used."""

    @asynccontextmanager
    async def lifespan(app):
        app.state.db = db or Database(settings.database_url)
        app.state.rate_limiter = RateLimiter()
        yield
        if db is None:
            await app.state.db.close()

    app = FastAPI(title="FormelX", lifespan=lifespan, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie="formelx_session",
        max_age=SESSION_MAX_AGE,
        same_site="lax",
        https_only=settings.secure_cookies,
    )
    # Added last = runs first: reject oversized and cross-site requests before anything else,
    # and put the security headers on every response, including errors.
    app.add_middleware(SameOriginMiddleware)
    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware, hsts=settings.secure_cookies)

    @app.exception_handler(DatabaseConnectionError)
    async def connection_error(request: Request, exc: DatabaseConnectionError):
        return JSONResponse({"detail": "connection_error"}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    @app.exception_handler(DatabaseError)
    async def database_error(request: Request, exc: DatabaseError):
        return JSONResponse({"detail": "database_error"}, status_code=status.HTTP_502_BAD_GATEWAY)

    for router in (auth.router, groups.router, elements.router, categories.router,
                   entries.compounds_router, entries.questions_router):
        app.include_router(router)

    # Everything that isn't an API route is the static frontend.
    app.mount("/", FrontendFiles(directory=FRONTEND_DIR, html=True), name="frontend")

    return app
