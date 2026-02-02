# FedEx International Fuel Surcharge Scraper  
**Playwright · Python · asyncio**

A small but complete web-scraping project that demonstrates how to reliably extract data from a modern, dynamic website using **Playwright (Python)** and **asyncio**.

The script navigates the FedEx surcharge page, handles cookie consent and geo-location modals, interacts with dynamic UI elements, and extracts structured data from a table.

---

## ✨ What this project demonstrates

- Browser automation with **Playwright (Python, async API)**
- Handling **cookie consent banners** (Usercentrics, including iframe cases)
- Handling **geo-location / language modals**
- Interaction with **dynamic content**
  - switching tabs (“International Fuel Surcharge”)
  - expanding hidden rows (“Show all weeks”)
- Reliable **table data extraction**
- Saving results to:
  - structured **JSON**
  - **PNG screenshot** of the table
- Clean, readable async code with separated helper functions

---

## 📂 Project structure
fedex-surcharge-scraper/
├─ scrape_fedex.py
├─ README.md
├─ requirements.txt
├─ .gitignore
└─ (optional)
├─ example_surcharges.json
└─ example_table.png


---

## 🧰 Requirements

- **Python 3.10+** (3.11 / 3.12 recommended)
- **Playwright ≥ 1.42**

---

## ⚙️ Installation

Create and activate a virtual environment:

```bash
python -m venv .venv


Windows (PowerShell):

.venv\Scripts\Activate.ps1


macOS / Linux:

source .venv/bin/activate


Install dependencies and Playwright browsers:

pip install -r requirements.txt
python -m playwright install


In corporate environments (proxy / firewall), you may need:

python -m playwright install chromium

▶️ Running the scraper
python scrape_fedex.py
