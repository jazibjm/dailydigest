"""
The shared shape of a fetched story, plus the source registry.

StoryItem is a plain dataclass (not the SQLAlchemy model) -- it's what sources
hand back before anything is summarized or saved.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

_SOURCES: list[Callable[[], list["StoryItem"]]] = []


@dataclass
class StoryItem:
    title: str
    url: str
    source: str       # e.g. "hackernews", "rss:arstechnica"
    score: int = 0    # popularity signal where available, else 0
    # When the story was published (UTC, timezone-aware). None if unknown.
    published: datetime | None = None


def register(fetcher: Callable[[], list["StoryItem"]]):
    """Decorator: add a fetcher to the registry the pipeline iterates over."""
    _SOURCES.append(fetcher)
    return fetcher


def fetch_all_sources() -> list[StoryItem]:
    """
    Run every registered source and concatenate their stories.

    A failing source logs and is skipped rather than killing the whole run.
    Dedup happens later, in the pipeline.
    """
    items: list[StoryItem] = []
    for fetcher in _SOURCES:
        try:
            items.extend(fetcher())
        except Exception as exc:  # noqa: BLE001 - one bad feed shouldn't abort
            print(f"[sources] {fetcher.__name__} failed: {exc}")
    return items
