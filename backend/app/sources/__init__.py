"""
Source registry.

Every source is a function that returns a list of StoryItem. They register
themselves with @register, and the pipeline just calls fetch_all_sources().
Adding a source = write one function + decorate it (or, for RSS, add a URL to
RSS_FEEDS in config).
"""

from .base import StoryItem, register, fetch_all_sources

# Importing these modules runs their @register decorators, wiring them in.
from . import hackernews  # noqa: F401,E402
from . import rss  # noqa: F401,E402

__all__ = ["StoryItem", "register", "fetch_all_sources"]
