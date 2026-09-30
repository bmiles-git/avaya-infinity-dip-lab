from pathlib import Path
import re

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .auth import check_credentials, current_user, login_redirect, logout_redirect, safe_next
from .database import get_db
from .models import Customer, Patient, Vendor

STATIC_DIR = Path(__file__).resolve().parent / "static"
router = APIRouter()
ENTITY_MODELS = {
    "customer": (Customer, "customer_id"),
    "patient": (Patient, "patient_id"),
    "vendor": (Vendor, "vendor_id"),
}


def _render(name: str, **repl) -> HTMLResponse:
    html = (STATIC_DIR / name).read_text(encoding="utf-8")
    for key, value in repl.items():
        token = "{" + "{" + key + "}" + "}"
        html = html.replace(token, value)
    return HTMLResponse(html)


def _row(obj) -> dict:
    data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    data.pop("id", None)
    return data


def _pin(value):
    if value is None:
        return None
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(4)[-4:] if digits else None


def _phone(value):
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if not digits:
        return None
    if len(digits) == 10:
        digits = "1" + digits
    return "+" + digits


def default_pin_for(entity: str, record_id: str) -> str:
    digits = re.sub(r"\D", "", record_id or "") or "0"
    n = int(digits[-4:] or "0")
    if entity == "patient":
        return f"{2000 + n:04d}"
    if entity == "vendor":
        return f"{3000 + n:04d}"
    return f"{1000 + n:04d}"


def _name(entity, rec):
    if entity == "vendor":
        return rec.company_name
    return f"{rec.first_name} {rec.last_name}".strip()


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request, next: str = "/admin", error: str = ""):
    if current_user(request):
        return RedirectResponse(safe_next(next), status_code=303)
    return _render("login.html", error=error, next=safe_next(next))


@router.post("/admin/login")
def admin_login(username: str = Form(...), password: str = Form(...), next: str = Form("/admin")):
    if check_credentials(username, password):
        return login_redirect(username, safe_next(next))
    return _render("login.html", error="Invalid username or password.", next=safe_next(next))


@router.get("/admin/logout")
def admin_logout():
    return logout_redirect()


@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if not current_user(request):
        return RedirectResponse("/admin/login", status_code=303)
    return _render("admin.html")
