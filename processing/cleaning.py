"""Pure functions for cleaning and normalizing source records."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def clean_text(value: Any) -> str | None:
    """Collapse whitespace and remove non-breaking spaces."""
    if value is None:
        return None
    cleaned = " ".join(str(value).replace("\xa0", " ").split())
    return cleaned or None


def strip_quotes(value: Any) -> str | None:
    """Remove matching curly quotation marks from text."""
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return cleaned.strip("“”‘’\"'")


def clean_price(raw: Any) -> float | None:
    """Extract the first numeric price value, including currency symbols."""
    if raw is None:
        return None
    text = str(raw).replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def clean_rating(raw: Any) -> int | None:
    """Convert a word rating such as ``Three`` to an integer from 1 to 5."""
    if raw is None:
        return None
    rating_text = clean_text(raw)
    if rating_text is None:
        return None

    words = re.findall(r"[A-Za-z]+", rating_text.lower())
    if words and words[-1] in RATING_MAP:
        return RATING_MAP[words[-1]]
    if rating_text.isdigit():
        rating = int(rating_text)
        return rating if rating in range(1, 6) else None
    return RATING_MAP.get(rating_text)


def clean_tags(raw: Any) -> str | None:
    """Normalize tag text, sort it, and join it with semicolons."""
    if not raw:
        return None
    tags = {clean_text(tag).lower() for tag in str(raw).split(";") if clean_text(tag)}
    return ";".join(sorted(tags)) or None


def normalize_url(raw: Any) -> str | None:
    """Normalize a URL and require an HTTP or HTTPS scheme."""
    if raw is None:
        return None
    url = clean_text(raw)
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url


def clean_record(record: dict[str, Any], scraped_at: str) -> dict[str, Any]:
    """Clean one raw record into the shared output schema."""
    name = clean_text(record.get("name_or_title"))
    source_url = normalize_url(record.get("source_url"))
    return {
        "source": record.get("source"),
        "source_url": source_url,
        "name_or_title": name,
        "category": clean_text(record.get("category")),
        "price": clean_price(record.get("price_raw")),
        "rating": clean_rating(record.get("rating_raw")),
        "author": clean_text(record.get("author")),
        "tags": clean_tags(record.get("tags")),
        "description": clean_text(record.get("description")),
        "scraped_at": scraped_at,
    }
