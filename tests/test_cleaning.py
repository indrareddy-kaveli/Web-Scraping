"""Tests for data cleaning functions."""

from processing.cleaning import (
    clean_price,
    clean_rating,
    clean_tags,
    clean_text,
    normalize_url,
)


def test_clean_text_collapses_whitespace_and_non_breaking_spaces():
    assert clean_text("  Hello\n\xa0World  ") == "Hello World"


def test_clean_price_extracts_currency_value():
    assert clean_price("£51.77") == 51.77


def test_clean_rating_accepts_words_and_numbers():
    assert clean_rating("star-rating Three") == 3
    assert clean_rating("5") == 5


def test_clean_tags_are_lowercase_and_sorted():
    assert clean_tags("Fiction; History; fiction") == "fiction;history"


def test_normalize_url_requires_http_scheme():
    assert normalize_url("https://example.com/book/1") == "https://example.com/book/1"
    assert normalize_url("ftp://example.com") is None
