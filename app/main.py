import os
from pathlib import Path
import re
from typing import Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Customer, Patient, Vendor
from .seed import customers as seed_customers
from .seed import patients as seed_patients
from .seed import vendors as seed_vendors

API_KEY = os.getenv("API_KEY", "").strip()
APP_VERSION = "1.0.0"

app = FastAPI(
    title="Avaya Infinity Data Dip Lab",
    description=(
        "Pre-seeded test database for Avaya Infinity workflow data dips. "
        "50 customers, 50 patients, and 50 vendors with predictable phone numbers."
    ),
    version=APP_VERSION,
)


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        if db.query(Customer).count() == 0:
            db.add_all([Customer(**row) for row in seed_customers()])
        if db.query(Patient).count() == 0:
            db.add_all([Patient(**row) for row in seed_patients()])
        if db.query(Vendor).count() == 0:
            db.add_all([Vendor(**row) for row in seed_vendors()])
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if not digits:
        return None
    if len(digits) == 10:
        digits = "1" + digits
    return "+" + digits


def row_to_dict(obj) -> dict[str, Any]:
    data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    data.pop("id", None)
    return data


def not_found(entity: str, criteria: dict) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"found": False, "entity": entity, "criteria": criteria, "record": None},
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "avaya-infinity-dip-lab", "version": APP_VERSION}


@app.get("/api/v1/catalog")
def catalog(db: Session = Depends(get_db), _: None = Depends(require_api_key)):
    """Quick reference of seeded IDs and phones for test scripts."""
    return {
        "counts": {
            "customers": db.query(Customer).count(),
            "patients": db.query(Patient).count(),
            "vendors": db.query(Vendor).count(),
        },
        "phone_plan": {
            "customers": "+15035551xxx  (xxx = 001-050)",
            "patients": "+15035552xxx  (xxx = 001-050)",
            "vendors": "+15035553xxx  (xxx = 001-050)",
            "customer_alt_every_5th": "+15035554xxx",
        },
        "examples": {
            "customer": {
                "phone": "+15035551001",
                "customer_id": "CUST-0001",
                "account_number": "ACC-100001",
            },
            "patient": {
                "phone": "+15035552001",
                "patient_id": "PAT-0001",
                "mrn": "MRN800001",
            },
            "vendor": {
                "phone": "+15035553001",
                "vendor_id": "VND-0001",
                "vendor_code": "V2001",
            },
        },
    }


@app.get("/api/v1/customers")
def list_or_find_customers(
    phone: str | None = None,
    customer_id: str | None = None,
    account_number: str | None = None,
    email: str | None = None,
    limit: int = Query(default=50, ge=1, le=50),
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    q = db.query(Customer)
    if phone or customer_id or account_number or email:
        found = find_customer(db, phone, customer_id, account_number, email)
        if not found:
            raise not_found(
                "customer",
                {
                    "phone": phone,
                    "customer_id": customer_id,
                    "account_number": account_number,
                    "email": email,
                },
            )
        return {"found": True, "entity": "customer", "count": 1, "records": [row_to_dict(found)]}
    rows = q.order_by(Customer.customer_id).limit(limit).all()
    return {"found": True, "entity": "customer", "count": len(rows), "records": [row_to_dict(r) for r in rows]}


@app.get("/api/v1/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db), _: None = Depends(require_api_key)):
    row = db.query(Customer).filter(Customer.customer_id == customer_id.upper()).first()
    if not row:
        raise not_found("customer", {"customer_id": customer_id})
    return {"found": True, "entity": "customer", "record": row_to_dict(row)}


@app.get("/api/v1/patients")
def list_or_find_patients(
    phone: str | None = None,
    patient_id: str | None = None,
    mrn: str | None = None,
    member_id: str | None = None,
    date_of_birth: str | None = None,
    limit: int = Query(default=50, ge=1, le=50),
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    q = db.query(Patient)
    if phone or patient_id or mrn or member_id or date_of_birth:
        found = find_patient(db, phone, patient_id, mrn, member_id, date_of_birth)
        if not found:
            raise not_found(
                "patient",
                {
                    "phone": phone,
                    "patient_id": patient_id,
                    "mrn": mrn,
                    "member_id": member_id,
                    "date_of_birth": date_of_birth,
                },
            )
        return {"found": True, "entity": "patient", "count": 1, "records": [row_to_dict(found)]}
    rows = q.order_by(Patient.patient_id).limit(limit).all()
    return {"found": True, "entity": "patient", "count": len(rows), "records": [row_to_dict(r) for r in rows]}


@app.get("/api/v1/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db), _: None = Depends(require_api_key)):
    row = db.query(Patient).filter(Patient.patient_id == patient_id.upper()).first()
    if not row:
        raise not_found("patient", {"patient_id": patient_id})
    return {"found": True, "entity": "patient", "record": row_to_dict(row)}


@app.get("/api/v1/vendors")
def list_or_find_vendors(
    phone: str | None = None,
    vendor_id: str | None = None,
    vendor_code: str | None = None,
    company_name: str | None = None,
    limit: int = Query(default=50, ge=1, le=50),
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    q = db.query(Vendor)
    if phone or vendor_id or vendor_code or company_name:
        found = find_vendor(db, phone, vendor_id, vendor_code, company_name)
        if not found:
            raise not_found(
                "vendor",
                {
                    "phone": phone,
                    "vendor_id": vendor_id,
                    "vendor_code": vendor_code,
                    "company_name": company_name,
                },
            )
        return {"found": True, "entity": "vendor", "count": 1, "records": [row_to_dict(found)]}
    rows = q.order_by(Vendor.vendor_id).limit(limit).all()
    return {"found": True, "entity": "vendor", "count": len(rows), "records": [row_to_dict(r) for r in rows]}


@app.get("/api/v1/vendors/{vendor_id}")
def get_vendor(vendor_id: str, db: Session = Depends(get_db), _: None = Depends(require_api_key)):
    row = db.query(Vendor).filter(Vendor.vendor_id == vendor_id.upper()).first()
    if not row:
        raise not_found("vendor", {"vendor_id": vendor_id})
    return {"found": True, "entity": "vendor", "record": row_to_dict(row)}


class DipRequest(BaseModel):
    entity: Literal["customer", "patient", "vendor", "auto"] = Field(
        default="auto",
        description="Record type to search. Use auto to search all tables.",
    )
    phone: str | None = None
    ani: str | None = Field(default=None, description="Alias for phone (Avaya ANI)")
    customer_id: str | None = None
    account_number: str | None = None
    email: str | None = None
    patient_id: str | None = None
    mrn: str | None = None
    member_id: str | None = None
    date_of_birth: str | None = None
    vendor_id: str | None = None
    vendor_code: str | None = None
    company_name: str | None = None


def find_customer(db: Session, phone=None, customer_id=None, account_number=None, email=None):
    q = db.query(Customer)
    filters = []
    norm = normalize_phone(phone)
    if norm:
        filters.append(or_(Customer.phone == norm, Customer.alt_phone == norm))
    if customer_id:
        filters.append(Customer.customer_id == customer_id.upper())
    if account_number:
        filters.append(Customer.account_number == account_number.upper())
    if email:
        filters.append(Customer.email == email.lower())
    if not filters:
        return None
    return q.filter(*filters).first()


def find_patient(db, phone=None, patient_id=None, mrn=None, member_id=None, date_of_birth=None):
    q = db.query(Patient)
    filters = []
    norm = normalize_phone(phone)
    if norm:
        filters.append(Patient.phone == norm)
    if patient_id:
        filters.append(Patient.patient_id == patient_id.upper())
    if mrn:
        filters.append(Patient.mrn == mrn.upper())
    if member_id:
        filters.append(Patient.member_id == member_id.upper())
    if date_of_birth:
        filters.append(Patient.date_of_birth == date_of_birth)
    if not filters:
        return None
    return q.filter(*filters).first()


def find_vendor(db, phone=None, vendor_id=None, vendor_code=None, company_name=None):
    q = db.query(Vendor)
    filters = []
    norm = normalize_phone(phone)
    if norm:
        filters.append(Vendor.phone == norm)
    if vendor_id:
        filters.append(Vendor.vendor_id == vendor_id.upper())
    if vendor_code:
        filters.append(Vendor.vendor_code == vendor_code.upper())
    if company_name:
        filters.append(Vendor.company_name.ilike(f"%{company_name}%"))
    if not filters:
        return None
    return q.filter(*filters).first()


@app.api_route("/api/v1/dip", methods=["GET", "POST"])
def data_dip(
    request: Request,
    payload: DipRequest | None = None,
    entity: str = "auto",
    phone: str | None = None,
    ani: str | None = None,
    customer_id: str | None = None,
    account_number: str | None = None,
    email: str | None = None,
    patient_id: str | None = None,
    mrn: str | None = None,
    member_id: str | None = None,
    date_of_birth: str | None = None,
    vendor_id: str | None = None,
    vendor_code: str | None = None,
    company_name: str | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    """Primary Avaya Infinity data-dip endpoint."""
    body = payload.model_dump() if payload else {}
    params = {
        "entity": (body.get("entity") or entity or "auto").lower(),
        "phone": body.get("phone") or body.get("ani") or phone or ani,
        "customer_id": body.get("customer_id") or customer_id,
        "account_number": body.get("account_number") or account_number,
        "email": body.get("email") or email,
        "patient_id": body.get("patient_id") or patient_id,
        "mrn": body.get("mrn") or mrn,
        "member_id": body.get("member_id") or member_id,
        "date_of_birth": body.get("date_of_birth") or date_of_birth,
        "vendor_id": body.get("vendor_id") or vendor_id,
        "vendor_code": body.get("vendor_code") or vendor_code,
        "company_name": body.get("company_name") or company_name,
    }

    targets = [params["entity"]] if params["entity"] != "auto" else ["customer", "patient", "vendor"]
    record = None
    matched = None
    for target in targets:
        if target == "customer":
            record = find_customer(
                db, params["phone"], params["customer_id"], params["account_number"], params["email"]
            )
        elif target == "patient":
            record = find_patient(
                db,
                params["phone"],
                params["patient_id"],
                params["mrn"],
                params["member_id"],
                params["date_of_birth"],
            )
        elif target == "vendor":
            record = find_vendor(
                db, params["phone"], params["vendor_id"], params["vendor_code"], params["company_name"]
            )
        else:
            raise HTTPException(status_code=400, detail="entity must be customer, patient, vendor, or auto")
        if record:
            matched = target
            break

    if not record:
        return JSONResponse(
            status_code=404,
            content={
                "found": False,
                "entity": params["entity"],
                "criteria": {k: v for k, v in params.items() if v},
                "record": None,
            },
        )

    data = row_to_dict(record)
    display_name = (
        f"{data.get('first_name', data.get('contact_first_name', ''))} "
        f"{data.get('last_name', data.get('contact_last_name', ''))}"
    ).strip() or data.get("company_name")

    return {
        "found": True,
        "entity": matched,
        "display_name": display_name,
        "phone": data.get("phone"),
        "record": data,
    }


STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", response_class=HTMLResponse)
def explorer():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")
