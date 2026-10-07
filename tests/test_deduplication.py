"""Tests for duplicate fingerprint behavior."""

from processing.deduplication import find_duplicates, make_fingerprint


def test_duplicate_detection_ignores_case_and_whitespace():
    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": "Example Book Title",
            "author": None,
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "  EXAMPLE BOOK TITLE  ",
            "author": None,
        },
    ]

    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 1
    assert make_fingerprint(records[0]) == make_fingerprint(records[1])


def test_quote_duplicate_uses_author_and_first_50_characters():
    first_fifty = "A" * 50
    records = [
        {
            "source": "Quotes to Scrape",
            "author": "Ada Lovelace",
            "name_or_title": first_fifty,
        },
        {
            "source": "Quotes to Scrape",
            "author": "Ada Lovelace",
            "name_or_title": first_fifty + "Different ending.",
        },
    ]

    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 1
