"""Book scraping with dynamic pagination."""

from __future__ import annotations

import logging
from typing import Any

import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import get_next_url, get_page

LOGGER = logging.getLogger(__name__)
SOURCE_NAME = "Books to Scrape"
START_URL = "https://books.toscrape.com/"


def parse_book(article: Any, page_url: str) -> dict[str, Any]:
    """Extract one raw book record from a product listing element."""
    title_link = article.select_one("h3 > a")
    price = article.select_one("p.price_color")
    rating = article.select_one("p.star-rating")
    title = title_link.get("title") if title_link else None
    source_url = title_link.get("href") if title_link else None
    if source_url:
        source_url = requests.compat.urljoin(page_url, source_url)

    return {
        "source": SOURCE_NAME,
        "source_url": source_url,
        "name_or_title": title,
        "category": None,
        "price_raw": price.get_text(" ", strip=True) if price else None,
        "rating_raw": " ".join(rating.get("class", [])) if rating else None,
        "author": None,
        "tags": None,
        "description": None,
        "scraped_at": None,
    }


def scrape_books(session: requests.Session) -> list[dict[str, Any]]:
    """Follow every book listing page until no next link remains."""
    records: list[dict[str, Any]] = []
    current_url: str | None = START_URL
    page_number = 0

    while current_url:
        page_number += 1
        LOGGER.info("Scraping book page %d: %s", page_number, current_url)
        try:
            response = get_page(session, current_url)
            soup = BeautifulSoup(response.text, "lxml")
            articles = soup.select("article.product_pod")
            for article in articles:
                try:
                    records.append(parse_book(article, current_url))
                except Exception:
                    LOGGER.exception("Failed to parse a book record on %s", current_url)

            current_url = get_next_url(soup, current_url)
        except requests.RequestException:
            LOGGER.exception("Failed to fetch book page %s", current_url)
            break
        except Exception:
            LOGGER.exception("Unexpected error while processing book page %s", current_url)
            break

    LOGGER.info("Collected %d raw book records from %d pages", len(records), page_number)
    return records
