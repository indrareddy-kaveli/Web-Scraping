"""Quote scraping with dynamic pagination."""

from __future__ import annotations

import logging
from typing import Any

import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import get_next_url, get_page

LOGGER = logging.getLogger(__name__)
SOURCE_NAME = "Quotes to Scrape"
START_URL = "https://quotes.toscrape.com/"


def parse_quote(quote: Any, page_url: str) -> dict[str, Any]:
    """Extract one raw quote record from a quote listing element."""
    text = quote.select_one("span.text")
    author = quote.select_one("small.author")
    tags = quote.select("a.tag")
    source_url = quote.select_one("a[href^='/author/']")

    return {
        "source": SOURCE_NAME,
        "source_url": requests.compat.urljoin(page_url, source_url["href"])
        if source_url and source_url.get("href")
        else page_url,
        "name_or_title": text.get_text(" ", strip=True) if text else None,
        "category": None,
        "price_raw": None,
        "rating_raw": None,
        "author": author.get_text(" ", strip=True) if author else None,
        "tags": ";".join(tag.get_text(" ", strip=True) for tag in tags),
        "description": None,
        "scraped_at": None,
    }


def scrape_quotes(session: requests.Session) -> list[dict[str, Any]]:
    """Follow every quote listing page until no next link remains."""
    records: list[dict[str, Any]] = []
    current_url: str | None = START_URL
    page_number = 0

    while current_url:
        page_number += 1
        LOGGER.info("Scraping quote page %d: %s", page_number, current_url)
        try:
            response = get_page(session, current_url)
            soup = BeautifulSoup(response.text, "lxml")
            quotes = soup.select("div.quote")
            for quote in quotes:
                try:
                    records.append(parse_quote(quote, current_url))
                except Exception:
                    LOGGER.exception("Failed to parse a quote record on %s", current_url)

            current_url = get_next_url(soup, current_url)
        except requests.RequestException:
            LOGGER.exception("Failed to fetch quote page %s", current_url)
            break
        except Exception:
            LOGGER.exception("Unexpected error while processing quote page %s", current_url)
            break

    LOGGER.info("Collected %d raw quote records from %d pages", len(records), page_number)
    return records
