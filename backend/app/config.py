"""
Central place for every environment-driven setting.

Nothing else in the app should read os.environ directly -- import from here so
there's one obvious list of what needs to be configured (mirrors .env.example).
"""

import os

# Load a local .env file if python-dotenv is installed. In production (systemd,
# Vercel) the variables are injected by the environment, so dotenv is optional.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# ---- Database ----
# postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/techdigest",
)

# ---- OpenAI ----
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
# Model used for summarization. gpt-4.1-nano is cheapest; swap freely.
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

# ---- Pipeline tuning ----
NUM_STORIES = int(os.environ.get("NUM_STORIES", "15"))   # stories per source
MAX_CHARS = int(os.environ.get("MAX_CHARS", "2000"))     # extracted text cap

# ---- RSS feeds ----
# Comma-separated list of feed URLs. Adding a feed = add a URL here.
RSS_FEEDS = [
    url.strip()
    for url in os.environ.get(
        "RSS_FEEDS",
        ",".join(
            [
                "https://feeds.arstechnica.com/arstechnica/index",
                "https://techcrunch.com/feed/",
                "https://www.theverge.com/rss/index.xml",
                "https://www.wired.com/feed/rss",
                "https://www.pcmag.com/feeds/rss/news",
                "https://www.technologyreview.com/feed/",
            ]
        ),
    ).split(",")
    if url.strip()
]

# ---- Delivery ----
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# ---- API / CORS ----
# Comma-separated origins allowed to call the API (your Vercel domain, etc.).
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
