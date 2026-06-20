# Deployment

Backend runs on your VPS (FastAPI under uvicorn behind nginx, pipeline via
cron). Frontend deploys to Vercel. This doc covers the backend; the frontend is
a standard Vercel import (see the README).

The plan: get the API live first, then point the frontend at it.

---

## 1. Postgres

You have two options. Pick one and set `DATABASE_URL` accordingly.

### Option A — Postgres on the VPS

```bash
sudo apt update && sudo apt install -y postgresql
sudo -u postgres psql <<'SQL'
CREATE DATABASE techdigest;
CREATE USER digest WITH PASSWORD 'change-me';
GRANT ALL PRIVILEGES ON DATABASE techdigest TO digest;
SQL
```

Then:
```
DATABASE_URL=postgresql+psycopg://digest:change-me@localhost:5432/techdigest
```

### Option B — Neon (managed, free tier)

Create a project at neon.tech, copy the connection string, and adapt it to the
psycopg driver:
```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

### Local development

Use the bundled compose file instead of installing Postgres:
```bash
docker compose up -d
```
This matches the default `DATABASE_URL` in `backend/.env.example`.

---

## 2. First run on the VPS

```bash
git clone <your-repo-url> dailydigest
cd dailydigest/backend

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env            # fill in DATABASE_URL, OPENAI_API_KEY, DISCORD_WEBHOOK_URL,
                     # and set ALLOWED_ORIGINS to your Vercel domain

# Creates the tables and generates today's first digest:
python run_pipeline.py
```

---

## 3. FastAPI under systemd

Create `/etc/systemd/system/digest-api.service` (adjust paths/user):

```ini
[Unit]
Description=Daily Tech Digest API
After=network.target postgresql.service

[Service]
User=youruser
WorkingDirectory=/home/youruser/dailydigest/backend
EnvironmentFile=/home/youruser/dailydigest/backend/.env
ExecStart=/home/youruser/dailydigest/backend/.venv/bin/uvicorn app.api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now digest-api
sudo systemctl status digest-api
curl http://127.0.0.1:8000/health   # {"status":"ok"}
```

---

## 4. nginx reverse proxy + HTTPS

Point `api.dogethanos.uk` (A record in Cloudflare → your VPS IP) at the app.

Create `/etc/nginx/sites-available/digest-api`:

```nginx
server {
    server_name api.dogethanos.uk;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and get a cert:
```bash
sudo ln -s /etc/nginx/sites-available/digest-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.dogethanos.uk
```

> Cloudflare note: if the record is proxied (orange cloud), set SSL/TLS mode to
> "Full (strict)". Easiest first-time setup is to leave the record "DNS only"
> (grey cloud) while certbot runs, then re-enable the proxy.

After this, `https://api.dogethanos.uk/digests` should return JSON.

---

## 5. Daily cron

Run the pipeline once a day (e.g. 07:00). Use the venv's Python so deps resolve:

```cron
0 7 * * * cd /home/youruser/dailydigest/backend && /home/youruser/dailydigest/backend/.venv/bin/python run_pipeline.py >> /home/youruser/digest.log 2>&1
```

Edit with `crontab -e`. The pipeline is idempotent, so a double-run is harmless.

---

## 6. Frontend (Vercel)

1. Import the repo in Vercel.
2. Set **Root Directory** to `frontend`.
3. Add env var `NEXT_PUBLIC_API_URL=https://api.dogethanos.uk`.
4. Deploy.

Then set `ALLOWED_ORIGINS` in the backend `.env` to your Vercel domain (e.g.
`https://yourapp.vercel.app`, plus any custom domain) and restart the API:
```bash
sudo systemctl restart digest-api
```
