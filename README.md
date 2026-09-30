# Avaya Infinity Data Dip Lab

Test database container for Avaya Infinity workflow data dips.

- 50 customers, 50 patients, 50 vendors
- 4-digit PIN on every account
- Login-protected admin page to search and edit records
- Single Docker image (FastAPI + SQLite)

Repo: https://github.com/bmiles-git/avaya-infinity-dip-lab

The public IP is not hardcoded. Use whatever address the cloud host assigns. Optionally set `PUBLIC_BASE_URL` in `.env`.

```bash
git clone https://github.com/bmiles-git/avaya-infinity-dip-lab.git
cd avaya-infinity-dip-lab
cp .env.example .env
docker compose up -d --build
```

## .env

```bash
HOST_PORT=8080
ADMIN_USER=admin
ADMIN_PASSWORD=ChangeMe!2026
SESSION_SECRET=long-random-string
# Leave blank to follow the host on each request.
# Or set the current cloud URL, for example:
# PUBLIC_BASE_URL=http://203.0.113.10:8080
PUBLIC_BASE_URL=
```

`/health` and `/api/v1/catalog` return `public_base_url` so Infinity examples always match the host you actually opened.

## URLs

Replace `HOST` with localhost or the current cloud IP/DNS.

- Dip tester: `http://HOST:8080/`
- Admin: `http://HOST:8080/admin`
- Docs: `http://HOST:8080/docs`
- Health: `http://HOST:8080/health`

Default admin login: `admin` / `ChangeMe!2026`

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
GET {PUBLIC_BASE_URL}/api/v1/dip?entity=customer&phone={{ani}}
```

PIN check after the IVR collects 4 digits:

```
GET {PUBLIC_BASE_URL}/api/v1/verify?entity=customer&phone={{ani}}&pin={{pin}}
```

Use `found` and `pin_ok` to branch.

## Deploy on a cloud Docker host

1. Clone this repo on the instance.
2. Open TCP 8080 in the provider firewall (and ufw if used).
3. Optional: put the instance URL in `.env` as `PUBLIC_BASE_URL`.
4. Run:

```bash
cd avaya-infinity-dip-lab
docker compose up -d --build
curl http://127.0.0.1:8080/health
```

Existing SQLite volumes keep data. Startup adds a pin column and fills empty PINs only.

## Persistence

SQLite is in the `dip-data` volume. `docker compose down` keeps it. `docker compose down -v` wipes it.
