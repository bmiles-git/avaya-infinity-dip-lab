"""Deterministic sample records for Avaya Infinity data-dip testing."""

FIRST_NAMES = [
    "Ava", "Liam", "Maya", "Noah", "Sofia", "Ethan", "Isla", "Owen", "Zoe", "Caleb",
    "Nora", "Julian", "Elena", "Mason", "Aria", "Leo", "Chloe", "Henry", "Luna", "Jack",
    "Camila", "Wyatt", "Harper", "Theo", "Layla", "Miles", "Stella", "Asher", "Ivy", "Grayson",
    "Ruby", "Ezra", "Quinn", "Adrian", "Piper", "Roman", "Hazel", "Felix", "Sadie", "Kai",
    "Willow", "Nolan", "Aurora", "Beau", "Ivy", "Silas", "June", "Dean", "Freya", "Hugo",
]

LAST_NAMES = [
    "Bennett", "Reyes", "Patel", "Nguyen", "Brooks", "Khan", "Morales", "Singh", "Walsh", "Kim",
    "Foster", "Garcia", "Chen", "Hughes", "Diaz", "Murray", "Shah", "Cole", "Ortiz", "Park",
    "Sullivan", "Rao", "Hayes", "Castillo", "Price", "Ali", "West", "Navarro", "Grant", "Ibarra",
    "Douglas", "Mehta", "Lane", "Vasquez", "Porter", "Yoon", "Blair", "Cruz", "Hale", "Santos",
    "Reed", "Ito", "Bowen", "Delgado", "Frost", "Nair", "Quinn", "Romero", "Steele", "Tanaka",
]

CITIES = [
    ("Portland", "OR"), ("Seattle", "WA"), ("Austin", "TX"), ("Denver", "CO"),
    ("Chicago", "IL"), ("Atlanta", "GA"), ("Boston", "MA"), ("Phoenix", "AZ"),
    ("Nashville", "TN"), ("Minneapolis", "MN"),
]

CUSTOMER_TIERS = ["bronze", "silver", "gold", "platinum"]
CUSTOMER_STATUSES = ["active", "active", "active", "past_due", "on_hold"]
LANGUAGES = ["en-US", "en-US", "en-US", "es-US", "en-US"]

PATIENT_DEPTS = ["Primary Care", "Cardiology", "Orthopedics", "Dermatology", "Pediatrics"]
INSURERS = ["Aetna", "Blue Cross", "Cigna", "UnitedHealthcare", "Kaiser"]
PHYSICIANS = [
    "Dr. Helen Park", "Dr. Marcus Cole", "Dr. Priya Shah", "Dr. James Walsh",
    "Dr. Ana Morales", "Dr. Kevin Chen",
]

VENDOR_CATEGORIES = ["IT Services", "Facilities", "Medical Supplies", "Telecom", "Staffing"]
VENDOR_PREFIXES = [
    "Northwind", "Summit", "Pacific", "Harbor", "Cedar", "Ironwood", "Lumen",
    "Atlas", "Redwood", "Granite",
]
VENDOR_TYPES = ["Labs", "Partners", "Supply", "Systems", "Group", "Solutions"]


def phone(offset: int, exchange: int) -> str:
    """NANP test numbers in the 555 exchange. Offset 1-50."""
    return f"+1503555{exchange:01d}{offset:03d}"


def customers() -> list[dict]:
    rows = []
    for i in range(1, 51):
        city, state = CITIES[(i - 1) % len(CITIES)]
        rows.append(
            {
                "customer_id": f"CUST-{i:04d}",
                "account_number": f"ACC-{100000 + i}",
                "first_name": FIRST_NAMES[i - 1],
                "last_name": LAST_NAMES[i - 1],
                "phone": phone(i, 1),
                "alt_phone": phone(i, 4) if i % 5 == 0 else None,
                "email": f"{FIRST_NAMES[i - 1].lower()}.{LAST_NAMES[i - 1].lower()}@example.com",
                "tier": CUSTOMER_TIERS[(i - 1) % len(CUSTOMER_TIERS)],
                "status": CUSTOMER_STATUSES[(i - 1) % len(CUSTOMER_STATUSES)],
                "balance_usd": round((i * 37.25) % 2500, 2),
                "open_tickets": i % 4,
                "last_order_id": f"ORD-2026-{i:04d}",
                "preferred_language": LANGUAGES[(i - 1) % len(LANGUAGES)],
                "city": city,
                "state": state,
                "vip": i % 10 == 0,
                "pin": f"{1000 + i:04d}",
            }
        )
    return rows


def patients() -> list[dict]:
    rows = []
    for i in range(1, 51):
        year = 1948 + ((i * 7) % 55)
        month = ((i * 3) % 12) + 1
        day = ((i * 5) % 27) + 1
        rows.append(
            {
                "patient_id": f"PAT-{i:04d}",
                "mrn": f"MRN{800000 + i}",
                "first_name": FIRST_NAMES[(i + 7) % 50],
                "last_name": LAST_NAMES[(i + 13) % 50],
                "phone": phone(i, 2),
                "email": f"patient{i:02d}@example.com",
                "date_of_birth": f"{year:04d}-{month:02d}-{day:02d}",
                "primary_physician": PHYSICIANS[(i - 1) % len(PHYSICIANS)],
                "department": PATIENT_DEPTS[(i - 1) % len(PATIENT_DEPTS)],
                "insurance": INSURERS[(i - 1) % len(INSURERS)],
                "member_id": f"INS-{200000 + i}",
                "next_appointment": f"2026-10-{((i % 27) + 1):02d}T{9 + (i % 8):02d}:00:00",
                "allergy_flag": i % 6 == 0,
                "high_priority": i % 11 == 0,
                "pin": f"{2000 + i:04d}",
            }
        )
    return rows


def vendors() -> list[dict]:
    rows = []
    for i in range(1, 51):
        company = f"{VENDOR_PREFIXES[(i - 1) % len(VENDOR_PREFIXES)]} {VENDOR_TYPES[(i - 1) % len(VENDOR_TYPES)]}"
        rows.append(
            {
                "vendor_id": f"VND-{i:04d}",
                "vendor_code": f"V{2000 + i}",
                "company_name": company,
                "contact_first_name": FIRST_NAMES[(i + 21) % 50],
                "contact_last_name": LAST_NAMES[(i + 29) % 50],
                "phone": phone(i, 3),
                "email": f"ap@{company.lower().replace(' ', '')}.example.com",
                "category": VENDOR_CATEGORIES[(i - 1) % len(VENDOR_CATEGORIES)],
                "status": "active" if i % 9 else "hold",
                "payment_terms": "Net 30" if i % 2 else "Net 45",
                "outstanding_po": f"PO-2026-{i:04d}" if i % 3 == 0 else None,
                "credit_limit_usd": 10000 + (i * 500),
                "pin": f"{3000 + i:04d}",
            }
        )
    return rows
