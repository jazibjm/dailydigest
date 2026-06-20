"""
Table definitions for the tech digest.

SQLAlchemy lets us define tables as Python classes and work with rows as objects
instead of writing raw SQL by hand.

Two tables:
  digests  - one row per day, holds the grouped summary text
  stories  - the individual articles that fed each digest (many per digest)
"""

from datetime import date, datetime

from sqlalchemy import (
    func,
    ForeignKey,
    String,
    Integer,
    Text,
    Date,
    DateTime,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Every table class inherits from this base."""

    pass


class Digest(Base):
    __tablename__ = "digests"

    id: Mapped[int] = mapped_column(primary_key=True)
    digest_date: Mapped[date] = mapped_column(Date, unique=True)  # one per day
    summary: Mapped[str] = mapped_column(Text)                    # grouped markdown
    model: Mapped[str] = mapped_column(String(50))               # which LLM made it
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # One digest has many stories. back_populates links the two sides together.
    stories: Mapped[list["Story"]] = relationship(
        back_populates="digest", cascade="all, delete-orphan"
    )


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    digest_id: Mapped[int] = mapped_column(ForeignKey("digests.id"))
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50))
    score: Mapped[int] = mapped_column(Integer, default=0)

    # The other side of the relationship: each story belongs to one digest.
    digest: Mapped["Digest"] = relationship(back_populates="stories")
