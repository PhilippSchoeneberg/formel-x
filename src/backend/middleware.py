"""HTTP hardening: security headers, a same-origin check for writes and a request size limit.

All three are plain ASGI middleware, so they also cover the static frontend and error responses.
"""

import json
from urllib.parse import urlsplit

from starlette.exceptions import HTTPException


# Only our own files: no inline scripts or styles, no third-party code, no framing.
# The frontend sets dynamic styles through element.style (CSSOM), which CSP allows.
CONTENT_SECURITY_POLICY = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self'",
    "frame-ancestors 'none'",
])

SECURITY_HEADERS = {
    "content-security-policy": CONTENT_SECURITY_POLICY,
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "same-origin",
    "permissions-policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
}

# The interactive API docs load Swagger UI from a CDN with inline scripts; they get no CSP.
DOCS_PATHS = ("/api/docs", "/api/docs/oauth2-redirect")

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# The largest legitimate request (a question with five answers) is a few KiB.
MAX_BODY_BYTES = 64 * 1024


async def _send_json(send, status, detail):
    body = json.dumps({"detail": detail}).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
    })
    await send({"type": "http.response.body", "body": body})


def _header(scope, name):
    for key, value in scope.get("headers", []):
        if key == name:
            return value.decode("latin-1")
    return None


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app
        # No HSTS here: the TLS-terminating proxy (Caddy) sets it. Sending it from both would
        # duplicate the header.
        self.headers = dict(SECURITY_HEADERS)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        skip_csp = scope["path"] in DOCS_PATHS

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                existing = {key.lower() for key, _ in message.get("headers", [])}
                extra = [
                    (key.encode(), value.encode()) for key, value in self.headers.items()
                    if key.encode() not in existing and not (skip_csp and key == "content-security-policy")
                ]
                message = {**message, "headers": [*message.get("headers", []), *extra]}
            await send(message)

        await self.app(scope, receive, send_with_headers)


class SameOriginMiddleware:
    """Rejects state-changing API requests that a browser sends from another site (CSRF).

    The session cookie is SameSite=Lax already; this is a second, independent layer. Requests
    without Origin and Sec-Fetch-Site headers (curl, tests, server-to-server) are allowed:
    CSRF needs a victim's browser, and browsers always send at least one of them.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["method"] in UNSAFE_METHODS and scope["path"].startswith("/api/"):
            origin = _header(scope, b"origin")
            fetch_site = _header(scope, b"sec-fetch-site")
            # Reverse proxies often rewrite Host (nginx's default is the upstream address) and
            # pass the original in X-Forwarded-Host. A page on another site can't set that
            # header (it's not CORS-safelisted), so accepting it doesn't weaken the check.
            hosts = {_header(scope, b"host")}
            forwarded = _header(scope, b"x-forwarded-host")
            if forwarded:
                hosts.add(forwarded.split(",")[0].strip())
            if origin is not None and origin != "null":
                if urlsplit(origin).netloc not in hosts:
                    return await _send_json(send, 403, "cross_origin_request")
            elif origin == "null" or fetch_site in ("cross-site", "same-site"):
                return await _send_json(send, 403, "cross_origin_request")
        await self.app(scope, receive, send)


class _BodyTooLarge(HTTPException):
    # An HTTPException, so FastAPI passes it through while parsing the body (it turns other
    # errors there into a generic 400) and answers 413 itself.
    def __init__(self):
        super().__init__(413, "request_too_large")


class BodySizeLimitMiddleware:
    """Answers 413 for bodies over MAX_BODY_BYTES instead of reading them into memory."""

    def __init__(self, app, max_bytes=MAX_BODY_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        length = _header(scope, b"content-length")
        if length is not None and (not length.isdigit() or int(length) > self.max_bytes):
            return await _send_json(send, 413, "request_too_large")

        # Chunked bodies have no Content-Length: count while reading.
        received = 0
        response_started = False

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _BodyTooLarge
            return message

        async def tracking_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracking_send)
        except _BodyTooLarge:
            if not response_started:
                await _send_json(send, 413, "request_too_large")
