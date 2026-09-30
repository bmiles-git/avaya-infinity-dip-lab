from pathlib import Path

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
        html = html.replace("{{' + key + '}}".replace("{{'", "{{").replace("' + key + '}}", "}}"), value)
    return HTMLResponse(html)
