"""
Summarization via the OpenAI chat.completions API.

Takes the fetched stories, extracts each article's text, and asks the model to
group everything into topic categories. Returns (summary_markdown, model_name).
"""

from datetime import date

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL
from .extraction import extract_text
from .sources import StoryItem


def _build_prompt(stories: list[StoryItem], digest_date: date) -> str:
    blocks = []
    for i, story in enumerate(stories, 1):
        body = extract_text(story.url)
        snippet = body if body else "(could not extract article text)"
        blocks.append(
            f"[{i}] {story.title}\n"
            f"URL: {story.url}\n"
            f"Source: {story.source}\n"
            f"Points: {story.score}\n"
            f"Content: {snippet}\n"
        )
    articles = "\n".join(blocks)
    pretty_date = f"{digest_date:%A, %B} {digest_date.day}, {digest_date.year}"
    return (
        f"You are my personal tech news editor. Today is {pretty_date}. "
        "Below are the day's stories with extracted article text.\n\n"
        "Write the digest in GitHub-flavored markdown with two parts:\n\n"
        "1. Start with a short overview paragraph (3-5 sentences, no heading). "
        "It must be specific to what actually happened today: name the concrete "
        "developments -- the companies, products, people, and numbers from the "
        "stories below. Lead with the single biggest story. Do NOT write generic "
        "filler like 'today's tech landscape spans a broad spectrum' or vague "
        "statements about themes; every sentence should point to a real story "
        "from the list.\n\n"
        "2. Then group the stories into topic categories (for example: AI, "
        "Security, Hardware, Dev Tools, Business, Other) under '## ' headings. "
        "Under each category, give a one to two sentence summary of each story "
        "in plain language, and link the story title to its URL in markdown. "
        "Skip categories with no stories. Keep this part skimmable.\n\n"
        f"{articles}"
    )


def summarize(stories: list[StoryItem], digest_date: date) -> tuple[str, str]:
    """Return (markdown_summary, model_name)."""
    # Pass the key explicitly so misconfiguration fails loudly and early.
    client = OpenAI(api_key=OPENAI_API_KEY or None)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": _build_prompt(stories, digest_date)}],
    )
    return response.choices[0].message.content, OPENAI_MODEL
