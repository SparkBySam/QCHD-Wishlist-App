"""
Queen City Harley inventory scraper.

Adapted from PhotoGetApp / SearchInventoryPhotos.py:
- Uses Selenium + BeautifulSoup to paginate dealership inventory
- Returns every active listing (not only bikes missing photos)
- Skips sale-pending / sold units

Requires Chrome (or Chromium) installed; Selenium Manager resolves the driver.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

BASE_URL = "https://www.queencityharley.com"
INVENTORY_URL = BASE_URL + "/--inventory?layout=grid&pg={}"

# Safety limits (auto-pagination)
MAX_PAGES = 50
EMPTY_PAGE_LIMIT = 5
DUP_SIGNATURE_LIMIT = 2
MAX_SECONDS = 600
PAGE_LOAD_TIMEOUT = 12


@dataclass
class ScrapedBike:
    stock_number: str
    model_name: str
    year: int
    color: str = ""


def _listings_signature(soup: BeautifulSoup) -> str:
    try:
        ids = [li.get("data-unit-id", "") for li in soup.select("li[data-unit-id]")]
        return ",".join(ids)
    except Exception:
        return ""


def _is_sale_pending_or_sold(listing) -> bool:
    overlay = listing.select_one("span.vehicle-image__overlay-text")
    if overlay and "sale pending" in overlay.get_text(strip=True).lower():
        return True
    text = listing.get_text().lower()
    return "sale pending" in text or "sold" in text


def _parse_listing(listing) -> ScrapedBike | None:
    if _is_sale_pending_or_sold(listing):
        return None

    name_link = listing.select_one("a.vehicle-heading__link")
    year_text = ""
    make = ""
    model = ""

    if name_link:
        year_el = name_link.select_one("span.vehicle-heading__year")
        make_el = name_link.select_one("span.vehicle-heading__name")
        model_el = name_link.select_one("span.vehicle-heading__model")
        year_text = year_el.get_text(strip=True) if year_el else ""
        make = make_el.get_text(strip=True) if make_el else ""
        model = model_el.get_text(strip=True) if model_el else ""

    stock_el = listing.select_one(
        "li.vehicle-specs__item--stock-number span.vehicle-specs__value"
    )
    stock_number = stock_el.get_text(strip=True).upper() if stock_el else ""
    if not stock_number or stock_number == "N/A":
        return None

    color_el = listing.select_one(
        "li.vehicle-specs__item--color span.vehicle-specs__value"
    )
    color = color_el.get_text(strip=True).title() if color_el else ""
    if color.upper() == "N/A":
        color = ""

    year_match = re.search(r"\d{4}", year_text)
    if not year_match:
        return None
    year = int(year_match.group(0))

    model_name = " ".join(part for part in (make, model) if part).strip()
    if not model_name:
        model_name = "Unknown"

    return ScrapedBike(
        stock_number=stock_number,
        model_name=model_name,
        year=year,
        color=color,
    )


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1200")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    )
    return webdriver.Chrome(options=options)


def _load_page(driver: webdriver.Chrome, page: int) -> None:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            driver.get(INVENTORY_URL.format(page))
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-unit-id]"))
            )
            return
        except Exception as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(1.0 + attempt * 0.8)
    if last_error:
        raise last_error


def run_scraper(
    start_page: int = 1,
    end_page: int | None = None,
) -> list[ScrapedBike]:
    """
    Scrape current Queen City Harley inventory.

    Args:
        start_page: First inventory page (1-based).
        end_page: Optional hard stop page. If None, auto-paginates until
            empty/duplicate pages or safety limits are hit.
    """
    start_page = max(1, start_page)
    fixed_total = end_page if end_page and end_page > 0 else None

    bikes_by_stock: dict[str, ScrapedBike] = {}
    empty_streak = 0
    dup_sig_streak = 0
    last_sig: str | None = None
    last_url: str | None = None
    start_time = time.time()
    page = start_page

    driver = _build_driver()
    try:
        while True:
            if fixed_total and page > fixed_total:
                logger.info("Reached end page %s", fixed_total)
                break
            if (page - start_page) >= MAX_PAGES:
                logger.warning("Hit max page safety limit (%s)", MAX_PAGES)
                break
            if (time.time() - start_time) > MAX_SECONDS:
                logger.warning("Hit max runtime safety limit (%ss)", MAX_SECONDS)
                break

            logger.info("Scraping inventory page %s", page)
            try:
                _load_page(driver, page)
            except Exception:
                # Empty / missing page in auto mode — count toward empty streak
                if fixed_total:
                    logger.exception("Failed to load page %s in fixed range", page)
                    page += 1
                    continue
                empty_streak += 1
                logger.info(
                    "No listings on page %s (load failed). Empty streak %s/%s",
                    page,
                    empty_streak,
                    EMPTY_PAGE_LIMIT,
                )
                if empty_streak >= EMPTY_PAGE_LIMIT:
                    break
                page += 1
                continue

            try:
                current_url = driver.current_url
            except Exception:
                current_url = None

            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.2)
            except Exception:
                pass

            soup = BeautifulSoup(driver.page_source, "html.parser")
            sig = _listings_signature(soup)

            if page > start_page and sig and sig == last_sig and not fixed_total:
                dup_sig_streak += 1
                logger.info(
                    "Page %s signature identical to previous (%s/%s)",
                    page,
                    dup_sig_streak,
                    DUP_SIGNATURE_LIMIT,
                )
                if dup_sig_streak >= DUP_SIGNATURE_LIMIT:
                    break
            else:
                dup_sig_streak = 0
            last_sig = sig

            if (
                page > start_page
                and current_url
                and last_url
                and current_url == last_url
                and not fixed_total
            ):
                dup_sig_streak += 1
                logger.info(
                    "URL unchanged on page %s (%s/%s)",
                    page,
                    dup_sig_streak,
                    DUP_SIGNATURE_LIMIT,
                )
                if dup_sig_streak >= DUP_SIGNATURE_LIMIT:
                    break
            last_url = current_url

            listings = soup.select("li[data-unit-id]")
            if not listings:
                if fixed_total:
                    logger.info("No listings on page %s (fixed range)", page)
                    page += 1
                    continue
                empty_streak += 1
                logger.info(
                    "No listings on page %s. Empty streak %s/%s",
                    page,
                    empty_streak,
                    EMPTY_PAGE_LIMIT,
                )
                if empty_streak >= EMPTY_PAGE_LIMIT:
                    break
                page += 1
                continue

            empty_streak = 0
            added = 0
            for listing in listings:
                bike = _parse_listing(listing)
                if bike is None:
                    continue
                if bike.stock_number not in bikes_by_stock:
                    bikes_by_stock[bike.stock_number] = bike
                    added += 1

            logger.info(
                "Page %s: %s listings, %s new stock numbers",
                page,
                len(listings),
                added,
            )
            page += 1
    finally:
        driver.quit()

    results = list(bikes_by_stock.values())
    logger.info("Scrape complete: %s unique bikes", len(results))
    return results
