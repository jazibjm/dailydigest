"""
Database engine and session wiring.

Kept separate from models.py so the table definitions don't drag the connection
setup along with them (matters for tests and for the FastAPI dependency below).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL
from .models import Base

# The engine is the connection pool to Postgres. Created once, reused everywhere.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# A session is one unit of work with the database. Open a fresh one per task.
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create the tables if they don't exist yet. Safe to run every time."""
    Base.metadata.create_all(engine)


def get_db():
    """FastAPI dependency: yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
