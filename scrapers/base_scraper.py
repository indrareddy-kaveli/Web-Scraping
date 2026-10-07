"""Shared HTTP session and request handling for the scraping pipeline."""

from __future__ import annotations

import logging
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 15
REQUEST_DELAY_SECONDS = 0.5
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


def create_session() -> requests.Session:
    """Create a configured session with retries for temporary server failures."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "WebScrapingAssignment/1.0 (learning project)",
            "Accept": "text/html,application/xhtml+xml",
        }
    )

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=1.0,
        status_forcelist=list(RETRY_STATUS_CODES),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_page(session: requests.Session, url: str) -> requests.Response:
    """Fetch a page, applying a polite delay and raising request failures."""
    response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    response.encoding = "utf-8"
    time.sleep(REQUEST_DELAY_SECONDS)
    return response


def get_next_url(soup: Any, current_url: str) -> str | None:
    """Return the next-page URL from the standard ``li.next > a`` selector."""
    next_link = soup.select_one("li.next > a")
    if not next_link or not next_link.get("href"):
        return None
    return requests.compat.urljoin(current_url, next_link["href"])
