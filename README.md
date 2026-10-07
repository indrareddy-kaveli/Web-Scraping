# Multi-Source Web Scraping & Data Consolidation

## Project overview

This project collects records from Books to Scrape and Quotes to Scrape, normalizes them into one CSV schema, validates them, removes duplicates, and writes a summary report and execution log.

The pipeline is:

`Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save`

## Python version

The assignment targets Python 3.10, 3.11, or 3.12. The current workspace was tested with Python 3.14.6; the source uses syntax and libraries compatible with the supported versions.

## Setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the complete pipeline:

```powershell
python main.py
```

Run tests without contacting either website:

```powershell
python -m pytest -q
```

## Data model

| Column | Books | Quotes |
|---|---|---|
| source | Books to Scrape | Quotes to Scrape |
| source_url | Book detail page | Author page URL |
| name_or_title | Book title | Quote text |
| category | Empty | Empty |
| price | Numeric price | Empty |
| rating | Integer 1-5 | Empty |
| author | Empty | Author name |
| tags | Empty | Semicolon-separated tags |
| description | Empty | Empty |
| scraped_at | UTC timestamp | UTC timestamp |

Book category and description are intentionally left empty because the listing page does not expose them. The application does not invent values.

## Scraping and pagination

Both source scrapers start at their home URLs and repeatedly inspect `li.next > a`. The returned relative URL is resolved with `urljoin`, so no page count is hard-coded. A failed page stops only that source; the other source continues.

The shared HTTP helper uses a `requests.Session`, a timeout, a User-Agent header, and retries for HTTP 429, 500, 502, 503, and 504. Requests are paused by 0.5 seconds between calls.

## Cleaning and validation

- Text is trimmed and whitespace and non-breaking spaces are collapsed.
- Prices are converted to floats after extracting the first numeric value.
- Ratings are converted from words such as `Three` or numeric strings to integers from 1 through 5.
- Tags are lowercased, sorted, and semicolon-separated.
- URLs must use HTTP or HTTPS and contain a host.
- Validation returns reasons for invalid records, allowing the summary to count each rejection type.

## Deduplication

Duplicates are removed. Books are identified by source and title. Quotes are identified by source, author, and the first 50 characters of the quote. The identity text is lowercased, punctuation is removed, whitespace is collapsed, and SHA-256 is used for a stable fingerprint.

## Outputs

- `output/final_dataset.csv`: one row per valid, unique record.
- `output/summary_report.json`: collected, cleaned, rejected, duplicate, final-count, and timing metrics.
- `logs/scraper.log`: timestamped request, page, warning, and error records.

The summary reconciliation condition is:

`collected - rejected - duplicates = final_record_count`

## Known limitations

- The websites may change their selectors or pagination markup.
- Book category and description are unavailable from the listing pages.
- A failed page causes that source to stop, while the other source continues.
- The assignment uses only the provided practice websites and does not attempt to bypass access controls.
