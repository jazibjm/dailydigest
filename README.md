# Daily Tech Digest

An automated daily tech-news digest. A Python pipeline pulls top stories from
Hacker News and RSS feeds, extracts article text, summarizes everything grouped
by topic with the OpenAI API, stores it in Postgres, and posts it to Discord. A
FastAPI service exposes the digests as JSON, and a Next.js frontend renders them.
<img width="1843" height="1290" alt="image" src="https://github.com/user-attachments/assets/0d058083-ad68-48dc-b847-98eb1761956f" />
<img width="1942" height="1289" alt="image" src="https://github.com/user-attachments/assets/0a01c035-110f-45ff-b98f-d885f5fc459e" />

```
backend/   Python pipeline + FastAPI  (runs on a VPS)
frontend/  Next.js App Router app      (deploys to Vercel)
docs/      deployment guide
```

## How it fits together

```
sources (HN, RSS) ─▶ dedupe by URL ─▶ extract text ─▶ summarize (OpenAI)
                                                            │
                          ┌─────────────────────────────────┤
                          ▼                                   ▼
                     Postgres                            Discord webhook
                          │
                          ▼
                  FastAPI  ─▶  Next.js frontend
```

The pipeline is **idempotent**: it skips if today's digest already exists, so
it's safe to run from cron repeatedly.

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # then fill in real values
```

Start a local Postgres (from the repo root):
```bash
docker compose up -d
```

Run the pipeline (creates tables on first run, generates a digest):
```bash
cd backend
python run_pipeline.py
```

Run the API:
```bash
uvicorn app.api:app --reload --port 8000
```

| Endpoint | Description |
|---|---|
| `GET /digests` | All digests (date + model), newest first |
| `GET /digests/latest` | Most recent digest with its stories |
| `GET /digests/{YYYY-MM-DD}` | A specific day's digest with its stories |
| `GET /health` | Health check |

### Adding a source

- **RSS feed:** add its URL to `RSS_FEEDS` in `.env` (comma-separated). Done.
- **A new kind of source:** write a function in `backend/app/sources/` that
  returns `list[StoryItem]`, decorate it with `@register`, and import it in
  `sources/__init__.py`. The pipeline picks it up automatically.

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local           # set NEXT_PUBLIC_API_URL
npm run dev                          # http://localhost:3000
```

## Configuration

Every setting is an environment variable; see `backend/.env.example` and
`frontend/.env.example` for the full list. **Never commit `.env`** — it's
gitignored from the first commit.

## Deployment

See [docs/deploy.md](docs/deploy.md): Postgres, a systemd unit for the API,
nginx + HTTPS, the daily cron line, and the Vercel import.
