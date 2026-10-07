"""Run the complete multi-source scraping and consolidation pipeline."""

from __future__ import annotations

import csv
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.base_scraper import create_session
from scrapers.books_scraper import scrape_books
from scrapers.quotes_scraper import scrape_quotes

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"
SOURCES = ("Books to Scrape", "Quotes to Scrape")
FIELDNAMES = (
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
)


def configure_logging() -> logging.Logger:
    """Configure the console and file logging handlers once."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(file_handler)

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("%(levelname)s: %(message)s")
        )
        logger.addHandler(stream_handler)

    return logger


def utc_timestamp() -> str:
    """Return the UTC timestamp used for every output record."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def scrape_source(
    scraper: Any, session: requests.Session, logger: logging.Logger
) -> list[dict[str, Any]]:
    """Run one source scraper and keep failures isolated from the other source."""
    try:
        return scraper(session)
    except Exception:
        logger.exception("Source scraper failed")
        return []


def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    """Write the fixed-schema CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def write_summary(summary: dict[str, Any], path: Path) -> None:
    """Write the machine-readable summary report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2, ensure_ascii=False)
        json_file.write("\n")


def run_pipeline() -> dict[str, Any]:
    """Run scraping, cleaning, validation, deduplication, and output writing."""
    logger = configure_logging()
    started_at = datetime.now(timezone.utc)
    session = create_session()
    raw_by_source: dict[str, list[dict[str, Any]]] = {}

    try:
        raw_by_source["Books to Scrape"] = scrape_source(scrape_books, session, logger)
        raw_by_source["Quotes to Scrape"] = scrape_source(scrape_quotes, session, logger)
    finally:
        session.close()

    cleaned: list[dict[str, Any]] = []
    rejected_by_reason: Counter[str] = Counter()
    cleaned_by_source = {source: 0 for source in SOURCES}
    scraped_at = utc_timestamp()

    for source in SOURCES:
        for raw_record in raw_by_source.get(source, []):
            cleaned_record = clean_record(raw_record, scraped_at)
            cleaned.append(cleaned_record)
            cleaned_by_source[source] += 1

            problems = validate_record(cleaned_record)
            if problems:
                rejected_by_reason.update(problems)
                logger.warning(
                    "Rejected record from %s: %s; record: %s",
                    source,
                    ", ".join(problems),
                    cleaned_record.get("name_or_title"),
                )

    unique_records, duplicates = find_duplicates(
        [record for record in cleaned if not validate_record(record)]
    )
    duplicates_by_source = Counter(record["source"] for record in duplicates)
    rejected_total = sum(rejected_by_reason.values())
    final_records = unique_records

    write_csv(final_records, CSV_PATH)
    ended_at = datetime.now(timezone.utc)
    summary = {
        "start_time": started_at.isoformat(timespec="seconds"),
        "end_time": ended_at.isoformat(timespec="seconds"),
        "duration_seconds": (ended_at - started_at).total_seconds(),
        "records_collected_per_source": {
            source: len(raw_by_source.get(source, [])) for source in SOURCES
        },
        "records_cleaned_per_source": cleaned_by_source,
        "records_rejected": {
            "total": rejected_total,
            "by_reason": dict(sorted(rejected_by_reason.items())),
        },
        "duplicates_detected": len(duplicates),
        "duplicates_by_source": dict(sorted(duplicates_by_source.items())),
        "final_record_count": len(final_records),
        "final_record_count_reconciles": (
            sum(len(raw_by_source.get(source, [])) for source in SOURCES)
            - rejected_total
            - len(duplicates)
            == len(final_records)
        ),
    }
    write_summary(summary, SUMMARY_PATH)
    logger.info("Pipeline completed: %d final records", len(final_records))
    return summary


if __name__ == "__main__":
    run_pipeline()
