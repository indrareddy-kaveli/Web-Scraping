# AI Usage

## Tools used

- GitHub Copilot Chat was used to plan the project structure, generate the initial implementation, and identify edge cases.
- GitHub Copilot code assistance was used to create and review the scraper, processing, test, and documentation files.

## Representative prompts

- “Create a Python ETL pipeline that scrapes Books to Scrape and Quotes to Scrape with reusable HTTP retries and dynamic pagination.”
- “Implement pure cleaning functions for prices, ratings, tags, URLs, and text without network access.”
- “Design normalized fingerprint logic for books and quotes and write tests for whitespace and capitalization differences.”
- “Create a main entry point that writes CSV, JSON, and logging outputs and keeps source failures isolated.”

## Changes after reviewing AI output

- Added explicit null checks before every optional HTML element.
- Added source-specific exception isolation so one source failure does not stop the other.
- Changed rating normalization to handle both the website's `star-rating Three` class and numeric ratings.
- Added an explicit reconciliation check in the summary report.
- Added tests that exercise the pure processing functions without making website requests.

## Mistakes found in AI suggestions

- An initial recommendation assumed that every `p.star-rating` class contained only a rating word; the page includes additional classes, so the implementation extracts the rating word from the full class string.
- A generated pagination example did not ensure that the source-specific parser could continue after a single malformed record.
- A generated summary did not include a reconciliation rule, so the final implementation includes one.

## Final verification

The complete pipeline was run with the installed environment, unit tests were run without network access, and generated CSV/JSON/log files were inspected. The final implementation was reviewed for selector safety, validation reasons, duplicate identity rules, retry behavior, and count reconciliation.
