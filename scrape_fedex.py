import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

URL = "https://www.fedex.com/en-hu/shipping/surcharges.html"

SCRIPT_DIR = Path(__file__).resolve().parent
SCREENSHOT_PATH = SCRIPT_DIR / "fedex_table.png"
JSON_OUTPUT_PATH = SCRIPT_DIR / "surcharges.json"

HEADLESS = False  # Zostaw False, żeby widzieć przeglądarkę


async def handle_location_modal(page):
    # Wybierz ENGLISH dla HU, jeśli pokaże się geolokalizacja
    try:
        await page.wait_for_timeout(800)
        loc = page.locator('a.fxg-geo-locator_link[data-country-code="hu"]:has-text("ENGLISH")')
        if await loc.count() > 0 and await loc.first.is_visible():
            await loc.first.click()
            await page.wait_for_load_state("networkidle")
            return
        close_btn = page.locator("[class*='geo-locator__modal_close'],[aria-label='close']")
        if await close_btn.count() > 0 and await close_btn.first.is_visible():
            await close_btn.first.click()
    except Exception:
        pass


async def handle_cookies(page):
    # Odrzuć/zaakceptuj baner cookies (również w iframie Usercentrics)
    try:
        for frame in page.frames:
            if "usercentrics" in (frame.url or ""):
                try:
                    await frame.locator("button[data-action='deny']").click(timeout=1500)
                    return
                except Exception:
                    for label in ["REJECT OPTIONAL COOKIES", "Reject optional cookies", "Reject all", "Reject"]:
                        try:
                            await frame.get_by_role("button", name=re.compile(label, re.I)).click(timeout=1200)
                            return
                        except Exception:
                            pass

        for sel in [
            "button[data-action='deny']",
            "button:has-text('REJECT OPTIONAL COOKIES')",
            "button:has-text('Reject optional cookies')",
            "button:has-text('Reject all')",
        ]:
            loc = page.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible():
                await loc.first.click(timeout=1500)
                return

        for sel in [
            "button[data-action='accept']",
            "button:has-text('ACCEPT ALL COOKIES')",
            "button:has-text('Accept all')",
        ]:
            loc = page.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible():
                await loc.first.click(timeout=1500)
                return
    except Exception:
        pass


async def click_show_all_weeks(page):
    # Kliknij „Show all weeks”, jeśli widoczne
    try:
        show_all = page.locator("text=Show all weeks")
        if await show_all.count() > 0 and await show_all.first.is_visible():
            await show_all.first.click()
            try:
                await page.locator("text=Show Less").wait_for(timeout=5000)
            except PlaywrightTimeout:
                await page.wait_for_timeout(1500)
    except Exception:
        pass


async def get_table_rows(page) -> List[Dict[str, str]]:
    # Upewnij się, że aktywna jest zakładka International Fuel Surcharge
    try:
        intl_tab = page.locator("a,button", has_text=re.compile(r"^\s*INTERNATIONAL FUEL SURCHARGE\s*$", re.I))
        if await intl_tab.count() > 0 and await intl_tab.first.is_visible():
            await intl_tab.first.click()
    except Exception:
        pass

    # Znajdź tabelę po nagłówku "Effective Date"
    table = page.locator("table").filter(has=page.locator("thead:has-text('Effective Date')")).first
    await table.wait_for(state="visible", timeout=15000)

    rows = table.locator("tbody tr")
    await rows.first.wait_for(state="visible", timeout=15000)

    data: List[Dict[str, str]] = []
    for i in range(await rows.count()):
        tds = rows.nth(i).locator("td")
        if await tds.count() < 3:
            continue
        effective = (await tds.nth(0).inner_text()).strip()
        usgc = (await tds.nth(1).inner_text()).strip()
        surcharge = (await tds.nth(2).inner_text()).strip()
        data.append(
            {
                "Effective date": re.sub(r"\s+", " ", effective),
                "USGC value": usgc,
                "Surcharge": surcharge,
            }
        )
    return data


async def save_table_screenshot(page, path: Path):
    # Nadpisz screenshot tabeli (jeśli istnieje)
    table = page.locator("table").filter(has=page.locator("thead:has-text('Effective Date')")).first
    await table.wait_for(state="visible", timeout=10000)
    await table.screenshot(path=str(path))


async def main():
    async with async_playwright() as pw:
        # Użyj domyślnego Chromium (bez wymuszania Edge)
        browser = await pw.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        await page.goto(URL, wait_until="domcontentloaded")
        await handle_location_modal(page)
        await handle_cookies(page)
        await page.wait_for_selector("text=International Fuel Surcharge", timeout=20000)
        await click_show_all_weeks(page)

        rows = await get_table_rows(page)

        # Podgląd w konsoli
        for r in rows:
            print(f"{r['Effective date']}\t{r['USGC value']}\t{r['Surcharge']}")

        # Nadpisz screenshot tabeli
        await save_table_screenshot(page, SCREENSHOT_PATH)
        print(f"Zapisano zrzut tabeli: {SCREENSHOT_PATH}")

        # Zapisz wyniki do JSON w tym samym folderze co skrypt
        JSON_OUTPUT_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Zapisano dane do JSON: {JSON_OUTPUT_PATH}")

        # Pauza – obejrzyj w przeglądarce i wciśnij Enter, aby zakończyć
        print("\nSprawdź dane w przeglądarce. Naciśnij Enter, aby zamknąć...")
        await asyncio.to_thread(input, "")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())