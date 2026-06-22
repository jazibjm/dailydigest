"""
The daily pipeline: fetch -> dedupe -> summarize -> save -> deliver.

Idempotent: if today's digest already exists it does nothing, so it's safe to
run from cron more than once a day.
"""

import sys
from datetime import date, datetime, timedelta, timezone

from .config import MAX_AGE_HOURS
from .db import SessionLocal, init_db
from .delivery.discord import post_digest
from .models import Digest, Story
from .sources import StoryItem, fetch_all_sources
from .summarization import summarize


def dedupe_by_url(stories: list[StoryItem]) -> list[StoryItem]:
    """Keep the first occurrence of each URL so we never summarize a dupe."""
    seen: set[str] = set()
    unique: list[StoryItem] = []
    for story in stories:
        if story.url in seen:
            continue
        seen.add(story.url)
        unique.append(story)
    return unique


def filter_recent(stories: list[StoryItem]) -> list[StoryItem]:
    """Drop stories older than MAX_AGE_HOURS so the digest is about today."""
    if not MAX_AGE_HOURS:
        return stories
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    # Keep stories newer than the cutoff. Unknown-date stories are kept so a
    # feed that omits timestamps doesn't silently vanish.
    return [s for s in stories if s.published is None or s.published >= cutoff]


def drop_already_seen(stories: list[StoryItem]) -> list[StoryItem]:
    """Drop URLs that appeared in any previous digest (cross-day dedup)."""
    session = SessionLocal()
    try:
        seen = {url for (url,) in session.query(Story.url).all()}
    finally:
        session.close()
    return [s for s in stories if s.url not in seen]


def already_ran_today() -> bool:
    """True if a digest for today already exists, so we don't duplicate."""
    session = SessionLocal()
    try:
        existing = session.query(Digest).filter_by(digest_date=date.today()).first()
        return existing is not None
    finally:
        session.close()


def save_digest(stories: list[StoryItem], summary: str, model: str) -> None:
    """Write one digest row plus its source stories to Postgres."""
    session = SessionLocal()
    try:
        digest = Digest(digest_date=date.today(), summary=summary, model=model)
        for story in stories:
            digest.stories.append(
                Story(
                    title=story.title,
                    url=story.url,
                    source=story.source,
                    score=story.score,
                )
            )
        session.add(digest)  # cascades to save the stories too
        session.commit()
    finally:
        session.close()


def run() -> None:
    init_db()  # create tables on first run, no-op afterwards

    if already_ran_today():
        print("Already generated a digest for today. Nothing to do.")
        return

    print("Fetching stories from all sources...")
    stories = dedupe_by_url(fetch_all_sources())
    if not stories:
        print("No stories found.")
        sys.exit(1)

    recent = filter_recent(stories)
    fresh = drop_already_seen(recent)
    print(
        f"{len(stories)} fetched -> {len(recent)} within {MAX_AGE_HOURS}h "
        f"-> {len(fresh)} not seen before."
    )
    if not fresh:
        # Valid state, not an error: nothing genuinely new since last digest.
        print("Nothing new to summarize today.")
        return

    print(f"Summarizing {len(fresh)} stories...")
    stories = fresh
    summary, model = summarize(stories, date.today())

    print("Saving to database...")
    save_digest(stories, summary, model)

    print("Delivering to Discord...")
    post_digest(summary)

    print("\n" + "=" * 60)
    print(f"TECH DIGEST - {date.today()}")
    print("=" * 60)
    print(summary)


if __name__ == "__main__":
    run()
