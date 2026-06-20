"""Article text extraction with trafilatura."""

import trafilatura

from .config import MAX_CHARS


def extract_text(url: str) -> str:
    """Pull the main article body. Returns empty string on failure."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    text = trafilatura.extract(downloaded) or ""
    return text[:MAX_CHARS]
