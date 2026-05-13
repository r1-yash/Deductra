# Deductra

Deductra is a small full-stack app that answers questions using **live web search** (retrieval) and an **LLM** (generation). Users sign in with **GitHub** via **Supabase Auth**; the backend can sync each user into a **PostgreSQL** database for your own tables and future features.

## Architecture

| Layer | Stack |
|--------|--------|
| Frontend | [Next.js](https://nextjs.org/) 16 (App Router), React 19, Tailwind CSS 4 |
| Auth | [Supabase](https://supabase.com/) (`@supabase/supabase-js`), GitHub OAuth |
| Backend | [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy, Alembic |
| Search | [Tavily](https://tavily.com/) |
| LLM | [Groq](https://groq.com/) (`llama-3.3-70b-versatile`) |
| Database | PostgreSQL (`DATABASE_URL`) |

Flow: the dashboard sends the user’s question to `POST /deductra_ask`. The API runs a Tavily search, builds a prompt from those results only, calls Groq, and returns an answer plus source URLs. After login, the client calls `POST /sync_user` so the backend can upsert the user by email (using the same UUID as Supabase Auth).

## Repository layout

```
deductra/
├── frontend/     # Next.js app
└── backend/      # FastAPI app, SQLAlchemy models, Alembic migrations
```

## Prerequisites

- Node.js 20+ (matches frontend tooling)
- Python 3.11+ recommended
- A [Supabase](https://supabase.com/) project with GitHub OAuth enabled and redirect URL pointing at your app (e.g. `http://localhost:3000/dashboard`)
- Tavily and Groq API keys
- PostgreSQL instance and a connection string for Alembic and the API

## Environment variables

### Frontend (`frontend/`)

Create `frontend/.env.local`:

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon (public) key |

### Backend (`backend/`)

Create `backend/.env` (or export in your shell):

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `TAVILY_API_KEY` | Tavily search API key |
| `GROQ_API_KEY` | Groq API key |

CORS is configured for `http://localhost:3000`.

## Setup

### Database

From `backend/`:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Apply migrations (requires `DATABASE_URL`):

```bash
alembic upgrade head
```

### Backend server

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

API base: `http://localhost:8000`. Docs: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Sign in with GitHub; you are redirected to `/dashboard` where you can ask questions.

The frontend currently calls `http://localhost:8000` for `sync_user` and `deductra_ask`. For production, point those URLs at your deployed API (or use env-based base URLs).

## Scripts

**Frontend**

- `npm run dev` — development server
- `npm run build` / `npm run start` — production build and serve
- `npm run lint` — ESLint

**Backend**

- `uvicorn main:app --reload --port 8000` — local API

## API overview

- `POST /sync_user` — body: `{ "id", "email", "name?" }`; creates a row in `users` if the email is new (id matches Supabase user UUID).
- `POST /deductra_ask` — body: `{ "query": "..." }`; returns `{ "answer", "sources" }` where `sources` is a list of `{ "url" }` from Tavily.

The model is instructed to return XML-like tags (`<ANSWER>`, `<question>`); the dashboard parses those for the main reply and follow-up chips.
