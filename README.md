# Avaya Infinity Data Dip Lab

Preconfigured Docker container with a sample database for **Avaya Infinity workflow data dips**.

Seeded on first start:

- 50 customers
- 50 patients
- 50 vendors

Built as a single container (FastAPI + SQLite) so it can run on a Linode Docker host with one command.

Repository: https://github.com/bmiles-git/avaya-infinity-dip-lab

```bash
git clone https://github.com/bmiles-git/avaya-infinity-dip-lab.git
cd avaya-infinity-dip-lab
docker compose up -d --build
```

## What this is for

Avaya Infinity workflows can call an external HTTP endpoint during an interaction to look up CRM / EHR / vendor data (a data dip). Point an Infinity HTTP or webhook module at this service and use the returned JSON fields as workflow variables.

This is a **test lab**, not a production CRM.

## Phone number plan

All numbers are fictional NANP `555` test numbers.

| Entity    | Phone range                 | Primary keys                         |
|-----------|-----------------------------|--------------------------------------|
| Customer  | `+15035551001` … `51050`    | `CUST-0001` / `ACC-100001`           |
| Patient   | `+15035552001` … `52050`    | `PAT-0001` / `MRN800001`             |
| Vendor    | `+15035553001` … `53050`    | `VND-0001` / `V2001`                 |

Every 5th customer also has an alternate phone: `+15035554xxx`.

Phone matching accepts `+15035551001`, `5035551001`, `503-555-1001`, and `(503) 555-1001`.

## Run locally

```bash
docker compose up -d --build
```

Open:

- Explorer UI: http://localhost:8080/
- OpenAPI docs: http://localhost:8080/docs
- Health: http://localhost:8080/health

Optional API key:

```bash
API_KEY=change-me HOST_PORT=8080 docker compose up -d --build
```

When `API_KEY` is set, send it as `X-API-Key`.

## Deploy on Linode

1. Create a Linode (Nanode 1 GB is enough). Ubuntu 24.04 + Docker Marketplace app is the fastest path.
2. Copy this folder to the instance, or clone it there.
3. Open TCP **8080** in the Linode Cloud Firewall (and `ufw` if enabled).
4. On the instance:

```bash
cd avaya-infinity-dip-lab
docker compose up -d --build
curl http://127.0.0.1:8080/health
```

5. In Avaya Infinity, set the workflow HTTP module URL to:

```text
http://YOUR_LINODE_PUBLIC_IP:8080/api/v1/dip
```

For anything beyond a closed lab, put HTTPS in front (Caddy, nginx, or Linode NodeBalancer + cert) and set `API_KEY`.

## Avaya Infinity workflow wiring

Use the workflow **HTTP / webhook** module.

### ANI lookup (most common)

```
GET http://YOUR_HOST:8080/api/v1/dip?entity=customer&phone={{ani}}
```

or

```
GET http://YOUR_HOST:8080/api/v1/dip?entity=auto&ani={{ani}}
```

`entity=auto` searches customers, then patients, then vendors.

### POST body (same module, JSON)

```json
{
  "entity": "patient",
  "ani": "{{ani}}",
  "mrn": "{{mrn}}"
}
```

### Suggested variable mapping

| JSON path                 | Workflow use                          |
|---------------------------|----------------------------------------|
| `found`                   | Branch: known vs unknown caller        |
| `entity`                  | Route by customer / patient / vendor   |
| `display_name`            | Prompt or screen-pop name              |
| `record.tier`             | VIP / gold queue                       |
| `record.status`           | Past-due vs active treatment           |
| `record.balance_usd`      | Billing IVR                            |
| `record.next_appointment` | Patient reminder flow                  |
| `record.allergy_flag`     | Clinical warning                       |
| `record.outstanding_po`   | Vendor AP queue                        |

A **404** response also includes `"found": false` so you can treat unknown ANI as a new-contact path.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `/api/v1/dip` | Primary data dip |
| GET | `/api/v1/customers` | List or filter customers |
| GET | `/api/v1/customers/{id}` | Customer by `CUST-00xx` |
| GET | `/api/v1/patients` | List or filter patients |
| GET | `/api/v1/patients/{id}` | Patient by `PAT-00xx` |
| GET | `/api/v1/vendors` | List or filter vendors |
| GET | `/api/v1/vendors/{id}` | Vendor by `VND-00xx` |
| GET | `/api/v1/catalog` | Counts and example keys |
| GET | `/health` | Liveness |

### Example curls

Customer by ANI:

```bash
curl "http://localhost:8080/api/v1/dip?entity=customer&phone=+15035551001"
```

Patient by MRN:

```bash
curl -X POST http://localhost:8080/api/v1/dip \
  -H "Content-Type: application/json" \
  -d '{"entity":"patient","mrn":"MRN800001"}'
```

Vendor by code:

```bash
curl "http://localhost:8080/api/v1/vendors?vendor_code=V2001"
```

Unknown number (expect 404 / found=false):

```bash
curl -i "http://localhost:8080/api/v1/dip?phone=+15035559999"
```

## Sample customer 1

```json
{
  "found": true,
  "entity": "customer",
  "display_name": "Ava Bennett",
  "phone": "+15035551001",
  "record": {
    "customer_id": "CUST-0001",
    "account_number": "ACC-100001",
    "tier": "bronze",
    "status": "active",
    "vip": false
  }
}
```

VIP customers are every 10th record (`CUST-0010`, `CUST-0020`, …). Past-due accounts follow the repeating status pattern `active, active, active, past_due, on_hold`.

## Persistence

SQLite lives in the `dip-data` Docker volume (`/app/data/dip_lab.db`). Recreating the container keeps the database unless you run `docker compose down -v`.

## Rebuild / load image on Linode

```bash
docker compose build
docker compose up -d
docker compose logs -f
```

To move a prebuilt image instead of building on the instance:

```bash
docker build -t avaya-infinity-dip-lab:1.0.0 .
docker save avaya-infinity-dip-lab:1.0.0 | gzip > avaya-infinity-dip-lab-1.0.0.tar.gz
# copy to Linode, then:
docker load < avaya-infinity-dip-lab-1.0.0.tar.gz
docker compose up -d
```
