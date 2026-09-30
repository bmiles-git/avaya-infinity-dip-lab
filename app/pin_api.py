import re

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import get_db
from .models import Customer, Patient, Vendor

router = APIRouter()


class VerifyBody(BaseModel):
    entity: str = "auto"
    phone: str | None = None
    ani: str | None = None
    pin: str | None = None
    customer_id: str | None = None
    account_number: str | None = None


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


def _row(obj):
    data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    data.pop("id", None)
    return data


def _name(data):
    return (f"{data.get('first_name', data.get('contact_first_name', ''))} {data.get('last_name', data.get('contact_last_name', ''))}").strip() or data.get("company_name")


def _find(db, entity, phone, pin, customer_id=None, account_number=None):
    targets = [entity] if entity != "auto" else ["customer", "patient", "vendor"]
    for target in targets:
        model = {"customer": Customer, "patient": Patient, "vendor": Vendor}[target]
        q = db.query(model)
        filters = []
        if phone:
            if target == "customer":
                filters.append(or_(model.phone == phone, model.alt_phone == phone))
            else:
                filters.append(model.phone == phone)
        if customer_id and target == "customer":
            filters.append(model.customer_id == customer_id.upper())
        if account_number and target == "customer":
            filters.append(model.account_number == account_number.upper())
        if pin and not phone and not customer_id and not account_number:
            filters.append(model.pin == pin)
        if not filters:
            continue
        rec = q.filter(*filters).first()
        if rec:
            return target, rec
    return None, None


@router.api_route("/api/v1/verify", methods=["GET", "POST"])
def verify_pin(payload: VerifyBody | None = None, entity: str = "auto", phone: str | None = None, ani: str | None = None, pin: str | None = None, customer_id: str | None = None, account_number: str | None = None, db: Session = Depends(get_db)):
    body = payload.model_dump() if payload else {}
    lookup_phone = _phone(body.get("phone") or body.get("ani") or phone or ani)
    lookup_pin = _pin(body.get("pin") or pin)
    lookup_entity = (body.get("entity") or entity or "auto").lower()
    if not lookup_pin:
        return JSONResponse(status_code=400, content={"found": False, "pin_ok": False, "reason": "pin_required"})
    target, rec = _find(db, lookup_entity, lookup_phone, lookup_pin, body.get("customer_id") or customer_id, body.get("account_number") or account_number)
    if not rec:
        return JSONResponse(status_code=404, content={"found": False, "pin_ok": False, "record": None})
    data = _row(rec)
    ok = _pin(data.get("pin")) == lookup_pin
    return {"found": True, "pin_ok": ok, "entity": target, "display_name": _name(data), "phone": data.get("phone"), "record": data if ok else None}
