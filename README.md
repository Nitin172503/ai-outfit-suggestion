# Outfit AI

**Live:** https://frontend-production-ac37.up.railway.app (click "View demo" — no signup needed)

Upload photos of clothes in your wardrobe, get outfit suggestions scored against a local
color-theory engine, and save the outfits you like into named libraries. Runs entirely
locally — no external AI service or dataset, just Pillow for pixel-level color extraction and
a from-scratch color-wheel rules engine.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL, JWT auth. No external API calls.
- **Frontend**: React + TypeScript (Vite), React Router.

## Features

- Email/password login (JWT-based).
- Upload wardrobe items as a single `.jpg`/`.png`, or a `.zip` of several images at once.
- On upload, dominant colors are extracted straight from the image's pixels (Pillow's
  median-cut quantizer — pure local computation, no network call, no pretrained model).
  Garment *category* (top, bottom, shoes, ...) has no reliable local-only detector, so you set
  that by hand from the Wardrobe page; color is filled in automatically either way.
- Outfit suggestions: pairs one item per key category (top/bottom/shoes, optionally
  outerwear) and ranks every combination purely by how well its colors score against the color
  engine. Fully deterministic and local — see `backend/app/services/suggestion_engine.py`.
- **Color book**: a from-scratch color-theory engine (`backend/app/services/color_engine.py`)
  that classifies any set of colors into monochromatic / analogous / complementary /
  split-complementary / triadic schemes, plus a curated set of named palettes. This is the same
  engine both the suggestion generator and the browsable "Color Book" page use, so they always
  agree.
- Save any outfit into a named library (collection); browse/delete by library.

## Backend setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in JWT_SECRET
```

Create the database (uses a local Postgres install — Homebrew's `postgresql` service,
Postgres.app, or similar; no Docker involved):

```bash
psql postgres -c "CREATE ROLE outfit LOGIN PASSWORD 'outfit'"
psql postgres -c "CREATE DATABASE outfit_ai OWNER outfit"
```

Run migrations, seed a demo account, and start the API:

```bash
alembic upgrade head
python seed_demo.py   # creates demo@outfitai.app / OutfitDemo123! with a sample wardrobe
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL defaults to http://localhost:8000
npm run dev
```

App: http://localhost:5173

## Demo account

`python seed_demo.py` creates a ready-to-explore account: **demo@outfitai.app** /
**OutfitDemo123!**, pre-loaded with a 13-item wardrobe, two libraries, and three saved
outfits. The login page also has a "View demo" button that signs into it directly — no
credentials to type. Re-run the script anytime to reset it back to its original state.

## Deployment

Deployed on Railway as three services in one project: `backend` (FastAPI, Nixpacks-built —
no Dockerfile), `frontend` (static Vite build served via `serve`), and a managed `Postgres`
plugin. Config lives in `backend/railway.json` and `frontend/railway.json`. The backend's
start command chains `alembic upgrade head && python seed_demo.py && uvicorn ...`, so every
deploy migrates the schema and resets the public demo account to a clean state.

To redeploy after changes (from the repo root, with the Railway CLI linked to this project):

```bash
railway up backend --path-as-root --service backend --ci
railway up frontend --path-as-root --service frontend --ci
```

If the backend's public URL ever changes, update `VITE_API_BASE_URL` on the frontend service
and `CORS_ORIGINS` on the backend service to match, then redeploy both.

## Notes

- Uploaded images are stored on disk under `backend/storage/wardrobe/<user_id>/` and served
  back via `/storage/...`. In production this currently lives on the backend container's
  ephemeral filesystem (survives restarts, not redeploys) — attaching a Railway volume at
  `/app/storage` would make it durable; a CLI bug blocked that at deploy time, so it's a
  follow-up, not a blocker (the seeded demo wardrobe is unaffected either way, since it's
  regenerated on every deploy).
- Zip uploads are capped (`MAX_ZIP_ENTRIES`, `MAX_UPLOAD_MB` in `.env`) and sanitized against
  zip-slip (paths are flattened, only `.jpg/.jpeg/.png` entries are accepted).
- Nothing in this app calls out to a third-party API — color extraction and outfit scoring are
  both pure local computation, so it works fully offline once dependencies are installed.
