"""Tests for validation behavior."""

from processing.validation import validate_record


def test_valid_record_has_no_problems():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalog/1.html",
        "name_or_title": "Example Book",
        "price": 12.5,
        "rating": 4,
    }
    assert validate_record(record) == []


def test_invalid_values_return_reasons():
    record = {
        "source": "Unknown",
        "source_url": "ftp://example.com",
        "name_or_title": "",
        "price": -1,
        "rating": 6,
    }
    assert validate_record(record) == [
        "unknown_source",
        "missing_name",
        "invalid_url",
        "invalid_price",
        "invalid_rating",
    ]
