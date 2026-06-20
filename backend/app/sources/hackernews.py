"""Hacker News source: top stories that link out to an article."""

import requests

from ..config import NUM_STORIES
from .base import StoryItem, register

HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def _get_item(story_id):
    """Fetch a single HN item. Returns None on failure."""
    try:
        return requests.get(HN_ITEM.format(story_id), timeout=10).json()
    except requests.RequestException:
        return None


@register
def fetch_hackernews() -> list[StoryItem]:
    """Return the first NUM_STORIES HN top stories that link to an article."""
    ids = requests.get(HN_TOP, timeout=10).json()
    stories: list[StoryItem] = []
    for story_id in ids:
        if len(stories) >= NUM_STORIES:
            break
        item = _get_item(story_id)
        if item and item.get("url") and item.get("type") == "story":
            stories.append(
                StoryItem(
                    title=item["title"],
                    url=item["url"],
                    source="hackernews",
                    score=item.get("score", 0),
                )
            )
    return stories
