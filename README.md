# Avaya Infinity Data Dip Lab

Test database container for Avaya Infinity workflow data dips.

- 50 customers, 50 patients, 50 vendors
- 4-digit PIN on every account
- Login-protected admin page to search and edit records
- Single Docker image (FastAPI + SQLite)

Repo: https://github.com/bmiles-git/avaya-infinity-dip-lab

```bash
git clone https://github.com/bmiles-git/avaya-infinity-dip-lab.git
cd avaya-infinity-dip-lab
docker compose up -d --build
```

## URLs

- Dip tester: http://localhost:8080/
- Admin: http://localhost:8080/admin
- Docs: http://localhost:8080/docs
- Health: http://localhost:8080/health

Default admin login: `admin` / `ChangeMe!2026`

Change it before exposing the host:

```bash
ADMIN_USER=admin ADMIN_PASSWORD='your-strong-password' SESSION_SECRET='long-random-string' docker compose up -d --build
```

## Phone and PIN plan

| Entity   | Phone range              | IDs                    | PIN       |
|----------|--------------------------|------------------------|-----------|
| Customer | +15035551001 to 51050    | CUST-0001 / ACC-100001 | 1001-1050 |
| Patient  | +15035552001 to 52050    | PAT-0001 / MRN800001   | 2001-2050 |
| Vendor   | +15035553001 to 53050    | VND-0001 / V2001       | 3001-3050 |

Example: Ava Bennett is +15035551001 with PIN 1001.

## Infinity wiring

ANI lookup:

```
GET http://YOUR_HOST:8080/api/v1/dip?entity=customer&phone={{ani}}
```

PIN check after the IVR collects 4 digits:

```
GET http://YOUR_HOST:8080/api/v1/verify?entity=customer&phone={{ani}}&pin={{pin}}
```

Use `found` and `pin_ok` to branch.

## Deploy on Linode

1. Clone this repo on the instance.
2. Open TCP 8080 in the Linode Cloud Firewall (and ufw if used).
3. Run:

```bash
cd avaya-infinity-dip-lab
docker compose up -d --build
curl http://127.0.0.1:8080/health
```

Existing SQLite volumes keep data. Startup adds a pin column and fills empty PINs only.

## Persistence

SQLite is in the `dip-data` volume. `docker compose down` keeps it. `docker compose down -v` wipes it.
