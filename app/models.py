from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    account_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    alt_phone: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    tier: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16))
    balance_usd: Mapped[float] = mapped_column(Float)
    open_tickets: Mapped[int] = mapped_column(Integer)
    last_order_id: Mapped[str] = mapped_column(String(32))
    preferred_language: Mapped[str] = mapped_column(String(16))
    city: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(8))
    vip: Mapped[bool] = mapped_column(Boolean)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    mrn: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), index=True)
    date_of_birth: Mapped[str] = mapped_column(String(10), index=True)
    primary_physician: Mapped[str] = mapped_column(String(64))
    department: Mapped[str] = mapped_column(String(64))
    insurance: Mapped[str] = mapped_column(String(64))
    member_id: Mapped[str] = mapped_column(String(32), index=True)
    next_appointment: Mapped[str] = mapped_column(String(32))
    allergy_flag: Mapped[bool] = mapped_column(Boolean)
    high_priority: Mapped[bool] = mapped_column(Boolean)


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    vendor_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(128), index=True)
    contact_first_name: Mapped[str] = mapped_column(String(64))
    contact_last_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))
    payment_terms: Mapped[str] = mapped_column(String(16))
    outstanding_po: Mapped[str | None] = mapped_column(String(32), nullable=True)
    credit_limit_usd: Mapped[int] = mapped_column(Integer)
