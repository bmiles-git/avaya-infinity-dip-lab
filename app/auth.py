import hashlib
import hmac
import os
import time
from urllib.parse import quote, unquote

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

ADMIN_USER = os.getenv("ADMIN_USER", "admin").strip() or "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe!2026").strip() or "ChangeMe!2026"
SESSION_SECRET = os.getenv("SESSION_SECRET", "dip-lab-change-this-session-secret").encode()
COOKIE_NAME = "dip_admin"
SESSION_TTL_SECONDS = 12 * 60 * 60


def check_credentials(username: str, password: str) -> bool:
    user_ok = hmac.compare_digest(username or "", ADMIN_USER)
    pass_ok = hmac.compare_digest(password or "", ADMIN_PASSWORD)
    return user_ok and pass_ok


def _sign(payload: str) -> str:
    return hmac.new(SESSION_SECRET, payload.encode(), hashlib.sha256).hexdigest()


def make_session_token(username: str) -> str:
    payload = f"{username}.{int(time.time())}"
    return f"{payload}.{_sign(payload)}"


def parse_session_token(token: str | None) -> str | None:
    if not token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    username, issued, signature = parts
    payload = f"{username}.{issued}"
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    try:
        issued_at = int(issued)
    except ValueError:
        return None
    if time.time() - issued_at > SESSION_TTL_SECONDS:
        return None
    if username != ADMIN_USER:
        return None
    return username


def current_user(request: Request) -> str | None:
    return parse_session_token(request.cookies.get(COOKIE_NAME))


def login_redirect(username: str, next_path: str = "/admin") -> RedirectResponse:
    if not next_path.startswith("/admin"):
        next_path = "/admin"
    response = RedirectResponse(next_path, status_code=303)
    response.set_cookie(
        COOKIE_NAME,
        make_session_token(username),
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )
    return response


def logout_redirect() -> RedirectResponse:
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


def safe_next(value: str | None) -> str:
    path = unquote(value or "/admin")
    if path.startswith("/admin"):
        return path
    return "/admin"
