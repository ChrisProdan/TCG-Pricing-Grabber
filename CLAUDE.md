# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Pokémon TCG card pricing lookup tool. `backend/sync.py` pulls set/card/price data from the
tcgcsv.com public API and syncs it into a local Postgres database. `backend/app.py` is a small
Flask API that serves card image URLs and prices out of that database. `frontend/` is a Vite +
React scaffold that is not yet implemented (its files are currently empty stubs).

## Backend setup & commands

Run all commands from `backend/`.

```bash
# Environment: Python 3.14 (see .venv/pyvenv.cfg) via a venv at backend/.venv
.venv\Scripts\activate          # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the Flask API (dev server)
python app.py

# Run the sync job (fetches groups/cards/prices from tcgcsv.com into Postgres)
python sync.py
```

There are no test files, lint config, or build scripts in this repo yet — don't assume `pytest`,
`ruff`, etc. are set up.

### Database

- Postgres database name: `Pokemon_Pricing_Information`, user `postgres`, host `localhost`, port
  `5432`. Connection params are hardcoded in both `app.py` and `sync.py` (only the password comes
  from the environment).
- Expected tables (no migration/schema files exist in the repo — they must already exist in the
  target DB):
  - `groupdata(groupid PK, setname, releasedate)` — one row per card set ("group" in TCGplayer's
    terms).
  - `carddata(productid PK, cardname, imageurl, groupid, price)` — one row per card.
- Required env var: `DB_PASSWORD`, loaded via `python-dotenv` from `backend/.env` (see
  `backend/.env.example`). `.env` is gitignored — never commit it.

### Notable pattern: t-string SQL

This codebase relies on Python 3.14's PEP 750 **template strings** (`t"..."`) combined with
`psycopg[binary]>=3.3`'s native t-string support to build parameterized queries, e.g.:

```python
cur.execute(t"SELECT groupid FROM groupdata WHERE setname={setName}")
```

This is *not* an f-string — psycopg intercepts the template and binds `{setName}` as a real query
parameter (safe from SQL injection), even though it reads like inline interpolation. When editing
queries, keep using `t"..."` (not `f"..."`) for any value coming from a request or external data,
and don't "simplify" these into string concatenation or `%s`-style manual parameterization.

## Architecture

**`sync.py`** — data ingestion, run manually/on a schedule (no scheduler is wired up yet):
- `updateGroups()`: fetches `https://tcgcsv.com/tcgplayer/3/groups` (category `3` = Pokémon) and
  upserts each set into `groupdata`.
- `updateCards()`: reads existing `groupid`s from `groupdata`, then for each group fetches
  `.../{groupId}/products` (card metadata) and `.../{groupId}/prices` (market prices) from
  tcgcsv.com, upserts into `carddata`, and updates prices. When a product has multiple price
  entries, the lowest non-null `marketPrice` is kept. A `time.sleep(0.5)` between groups throttles
  the upstream API.
- `backend/cache/` holds raw JSON dumps from prior API pulls (`groups.json`,
  `ProductsandPrices/{groupId}_Products.json`, `{groupId}_Prices.json`) — gitignored, used as local
  snapshots rather than a live source of truth.

**`app.py`** — read-only Flask API:
- Single route: `GET /<setName>/<cardName>` → looks up the set's `groupid` via `getSet()`, then
  queries `carddata` for that card's `imageurl` and `price`, returning JSON. Returns
  `{"error": "not found"}` with HTTP 404 for unknown sets/cards or DB errors (errors are swallowed,
  not logged).
- CORS is enabled globally via `flask-cors` since the frontend will call this API cross-origin
  during development.

**`frontend/`** — Vite + React scaffold; all source files are currently empty placeholders, not
yet wired to the backend API.
