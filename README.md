# TCG Pricing Grabber

A Pokémon TCG card pricing lookup tool. It syncs set, card, and price data from the public
[tcgcsv.com](https://tcgcsv.com) API into a local Postgres database, then serves card image URLs
and prices through a small Flask API. A Vite + React frontend is scaffolded but not yet
implemented.

## How it works

- **`backend/sync.py`** — data ingestion. Fetches Pokémon ("category 3") set and card data from
  tcgcsv.com and upserts it into Postgres.
- **`backend/app.py`** — a read-only Flask API that looks up a card's image URL and price by set
  name and card name.
- **`frontend/`** — a Vite + React scaffold intended to consume the Flask API; its source files
  are currently empty placeholders.

## Requirements

- Python 3.14 (t-string / PEP 750 support is required — see [t-string SQL](#t-string-sql) below)
- PostgreSQL, running locally, with a database already created
- Node.js (for the frontend scaffold, once implemented)

## Getting started

All backend commands are run from `backend/`.

### 1. Set up the virtual environment

```bash
cd backend
.venv\Scripts\activate          # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure the database connection

Copy `backend/.env.example` to `backend/.env` and set your Postgres password:

```
DB_PASSWORD=your_postgres_password
```

`.env` is gitignored — never commit it. All other connection parameters (database name, user,
host, port) are hardcoded in `app.py` and `sync.py`:

| Setting  | Value                          |
|----------|--------------------------------|
| Database | `Pokemon_Pricing_Information`  |
| User     | `postgres`                     |
| Host     | `localhost`                    |
| Port     | `5432`                         |

### 3. Create the database schema

No migration files exist in this repo yet, so the following tables must already exist in the
target database before running the sync job:

```sql
CREATE TABLE groupdata (
    groupid     INTEGER PRIMARY KEY,
    setname     TEXT,
    releasedate TIMESTAMP
);

CREATE TABLE carddata (
    productid INTEGER PRIMARY KEY,
    cardname  TEXT,
    imageurl  TEXT,
    groupid   INTEGER REFERENCES groupdata (groupid),
    rarity    TEXT,
    price     NUMERIC
);
```

### 4. Sync pricing data

```bash
python sync.py
```

This pulls every Pokémon set from `https://tcgcsv.com/tcgplayer/3/groups` into `groupdata`, then
for each set fetches its products (card metadata, including rarity) and prices from tcgcsv.com and
upserts them into `carddata`. When a card has multiple price entries, the lowest non-null
`marketPrice` is kept. A short delay between sets throttles requests to the upstream API. This is
a manual/on-demand script — no scheduler is wired up yet.

### 5. Run the API

```bash
python app.py
```

Starts the Flask dev server (defaults to `http://127.0.0.1:5000`, `debug=True`). CORS is enabled
globally so the frontend can call the API cross-origin during development.

## API reference

### `GET /<setName>/<cardName>`

Looks up a card's image URL and market price.

**Example:**

```
GET /Scarlet & Violet/Pikachu
```

**Success response — `200 OK`:**

```json
{
  "imageUrl": "https://...",
  "price": "12.34"
}
```

**Error response — `404 Not Found`:**

```json
{ "error": "not found" }
```

Returned when the set or card doesn't exist, or if a database error occurs (errors are currently
swallowed rather than logged).

## Project structure

```
TCG Pricing Grabber/
├── backend/
│   ├── app.py              # Flask API
│   ├── sync.py              # tcgcsv.com → Postgres sync job
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env                 # gitignored, holds DB_PASSWORD
│   └── cache/                # gitignored raw JSON dumps from prior API pulls
└── frontend/                 # Vite + React scaffold (not yet implemented)
```

`backend/cache/` stores raw JSON snapshots from previous tcgcsv.com pulls (`groups.json`,
`ProductsandPrices/{groupId}_Products.json`, `{groupId}_Prices.json}`) for local reference — it is
not used as a live data source.

## t-string SQL

This codebase relies on Python 3.14's **template strings** (PEP 750, `t"..."`) combined with
`psycopg[binary]>=3.3`'s native t-string support to build parameterized queries safely, e.g.:

```python
cur.execute(t"SELECT groupid FROM groupdata WHERE setname={setName}")
```

This looks like an f-string but isn't — psycopg intercepts the template and binds `{setName}` as a
real, escaped query parameter rather than interpolating it into the SQL text. Any query built from
request or external data should use `t"..."`, not `f"..."` or manual `%s`-style parameterization.

## Status / known gaps

- No test suite, lint config, or build scripts yet.
- No database migration/schema files — the schema above must be created manually.
- No scheduler for `sync.py` — it's run manually.
- Frontend source files are placeholders and not yet wired to the backend API.
- Errors in `app.py` are caught and swallowed (returned as a generic 404) rather than logged.
