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


def _need_admin(request: Request):
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Admin login required")


def _get_rec(db, entity, record_id):
    if entity not in ENTITY_MODELS:
        raise HTTPException(status_code=404, detail="Unknown entity")
    model, key = ENTITY_MODELS[entity]
    rec = db.query(model).filter(getattr(model, key) == record_id.upper()).first() or db.query(model).filter(getattr(model, key) == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return rec, key


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


@router.get("/admin/api/search")
def admin_search(request: Request, q: str = "", entity: str = "all", db: Session = Depends(get_db)):
    _need_admin(request)
    needle = (q or "").strip()
    targets = ENTITY_MODELS if entity == "all" else {entity: ENTITY_MODELS[entity]}
    results = []
    for name, (model, key) in targets.items():
        query = db.query(model)
        if needle:
            like = f"%{needle}%"
            clauses = [getattr(model, key).ilike(like), model.phone.ilike(like), model.pin.ilike(like), model.email.ilike(like)]
            if hasattr(model, "first_name"):
                clauses.extend([model.first_name.ilike(like), model.last_name.ilike(like)])
            if hasattr(model, "account_number"):
                clauses.append(model.account_number.ilike(like))
            if hasattr(model, "mrn"):
                clauses.append(model.mrn.ilike(like))
            if hasattr(model, "company_name"):
                clauses.append(model.company_name.ilike(like))
            if hasattr(model, "vendor_code"):
                clauses.append(model.vendor_code.ilike(like))
            query = query.filter(or_(*clauses))
        for rec in query.limit(50).all():
            results.append({"entity": name, "id": getattr(rec, key), "name": _name(name, rec), "phone": rec.phone, "pin": rec.pin})
    return {"count": len(results), "records": results}


@router.get("/admin/api/{entity}/{record_id}")
def admin_get(entity: str, record_id: str, request: Request, db: Session = Depends(get_db)):
    _need_admin(request)
    rec, key = _get_rec(db, entity, record_id)
    return {"entity": entity, "id": getattr(rec, key), "default_pin": default_pin_for(entity, getattr(rec, key)), "record": _row(rec)}


@router.put("/admin/api/{entity}/{record_id}")
def admin_update(entity: str, record_id: str, payload: dict, request: Request, db: Session = Depends(get_db)):
    _need_admin(request)
    rec, key = _get_rec(db, entity, record_id)
    locked = {"id", key}
    columns = {c.name for c in rec.__table__.columns}
    if "pin" in payload and payload["pin"] is not None:
        pin_n = _pin(str(payload["pin"]))
        if not pin_n or len(pin_n) != 4:
            raise HTTPException(status_code=400, detail="PIN must be 4 digits")
        payload["pin"] = pin_n
    if "phone" in payload and payload["phone"]:
        payload["phone"] = _phone(str(payload["phone"])) or payload["phone"]
    for flag in ("vip", "allergy_flag", "high_priority"):
        if flag in payload:
            payload[flag] = str(payload[flag]).lower() in {"1", "true", "yes", "on"}
    for field, value in payload.items():
        if field not in locked and field in columns:
            setattr(rec, field, value if value != "" else None)
    db.commit()
    db.refresh(rec)
    return {"entity": entity, "id": getattr(rec, key), "default_pin": default_pin_for(entity, getattr(rec, key)), "record": _row(rec)}
