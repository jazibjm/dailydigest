"""
RSS source: pulls entries from every feed in config.RSS_FEEDS.

Adding a feed is a one-line change -- append a URL to RSS_FEEDS (env var or the
default list in config.py). No code change needed here.
"""

from urllib.parse import urlparse

import feedparser

from ..config import NUM_STORIES, RSS_FEEDS
from .base import StoryItem, register


def _feed_label(feed_url: str) -> str:
    """Turn a feed URL into a short source tag, e.g. 'rss:arstechnica'."""
    host = urlparse(feed_url).netloc.replace("www.", "")
    name = host.split(".")[0] if host else "feed"
    return f"rss:{name}"


@register
def fetch_rss() -> list[StoryItem]:
    """Return up to NUM_STORIES entries from each configured feed."""
    stories: list[StoryItem] = []
    for feed_url in RSS_FEEDS:
        parsed = feedparser.parse(feed_url)
        label = _feed_label(feed_url)
        for entry in parsed.entries[:NUM_STORIES]:
            link = entry.get("link")
            title = entry.get("title")
            if not link or not title:
                continue
            # RSS has no popularity score; leave it at 0.
            stories.append(StoryItem(title=title, url=link, source=label))
    return stories
