"""
FastAPI app exposing the digests over JSON.

Endpoints:
  GET /digests          - list all digests (date + model), newest first
  GET /digests/latest   - most recent digest with its stories
  GET /digests/{date}   - a specific day's digest with its stories (YYYY-MM-DD)

CORS origins come from ALLOWED_ORIGINS so your Vercel domain can call it.
"""

from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import ALLOWED_ORIGINS
from .db import get_db
from .models import Digest

app = FastAPI(title="Daily Tech Digest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---- Response shapes ----
class StoryOut(BaseModel):
    title: str
    url: str
    source: str
    score: int

    class Config:
        from_attributes = True


class DigestSummary(BaseModel):
    """Lightweight: used for the list view (no stories, no full summary)."""

    digest_date: date
    model: str

    class Config:
        from_attributes = True


class DigestDetail(BaseModel):
    digest_date: date
    model: str
    summary: str
    stories: list[StoryOut]

    class Config:
        from_attributes = True


# ---- Endpoints ----
@app.get("/digests", response_model=list[DigestSummary])
def list_digests(db: Session = Depends(get_db)):
    return (
        db.query(Digest)
        .order_by(Digest.digest_date.desc())
        .all()
    )


@app.get("/digests/latest", response_model=DigestDetail)
def latest_digest(db: Session = Depends(get_db)):
    digest = db.query(Digest).order_by(Digest.digest_date.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail="No digests yet.")
    return digest


@app.get("/digests/{digest_date}", response_model=DigestDetail)
def get_digest(digest_date: date, db: Session = Depends(get_db)):
    digest = db.query(Digest).filter_by(digest_date=digest_date).first()
    if not digest:
        raise HTTPException(status_code=404, detail="No digest for that date.")
    return digest


@app.get("/health")
def health():
    return {"status": "ok"}
