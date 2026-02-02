# fedex-surcharge-scraper
"Automatic web scraper for FedEx international fuel surcharges"

# FedEx International Fuel Surcharge Scraper (Playwright + asyncio)

This project demonstrates:
- browser automation using Playwright (Python, asyncio),
- handling cookie banners (Usercentrics) and geo-location modals,
- interaction with a dynamic website (the “International Fuel Surcharge” tab, “Show all weeks”),
- extracting data from a table and saving it to JSON,
- capturing a screenshot of the table (PNG).

## Requirements
- Python 3.10+ (3.11 / 3.12 recommended)
- `playwright>=1.42`

## Installation

```bash
python -m venv .venv
