"""
Discord delivery: post the digest to a webhook.

Discord caps a single message at 2000 characters, so long digests are split
across multiple messages, breaking on line boundaries where possible.
"""

from datetime import date

import requests

from ..config import DISCORD_WEBHOOK_URL

DISCORD_LIMIT = 2000


def _chunk(text: str, limit: int = DISCORD_LIMIT) -> list[str]:
    """
    Split text into <=limit pieces, preferring to break on newlines.

    A single line longer than the limit is hard-split as a fallback.
    """
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        # A monster line that won't fit on its own: flush, then hard-split it.
        if len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(line), limit):
                chunks.append(line[i : i + limit])
            continue

        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit:
            chunks.append(current)
            current = line
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks


def post_digest(summary: str, digest_date: date | None = None) -> bool:
    """
    Post the digest to Discord. Returns False (and skips) if no webhook is set,
    so the pipeline can run fine without Discord configured.
    """
    if not DISCORD_WEBHOOK_URL:
        print("[discord] DISCORD_WEBHOOK_URL not set, skipping delivery.")
        return False

    header = f"**Tech Digest - {digest_date or date.today()}**"
    body = f"{header}\n\n{summary}"

    for part in _chunk(body):
        resp = requests.post(
            DISCORD_WEBHOOK_URL,
            # flags=4 is SUPPRESS_EMBEDS: stops Discord from generating a link
            # preview card for every URL, which otherwise clutters the digest.
            json={"content": part, "flags": 4},
            timeout=15,
        )
        resp.raise_for_status()
    return True
