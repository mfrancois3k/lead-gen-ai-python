"""
scraper.py — Yellow Pages scraper for local service businesses.

Uses requests + BeautifulSoup with polite crawl delays.
Supports multi-page scraping and returns structured lead dicts.
"""

import time
import random
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

# ── Browser-like headers to reduce bot detection ─────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.yellowpages.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def scrape_yellow_pages(niche: str, location: str, max_results: int = 50) -> list[dict]:
    """
    Scrape business listings from YellowPages.com.

    Args:
        niche:       Business type to search (e.g. 'Plumbers').
        location:    Geographic location (e.g. 'Dallas, TX').
        max_results: Max number of leads to return.

    Returns:
        List of lead dicts with keys:
        Business Name, Phone, Address, Website, Email,
        Rating, Review Count, Category, Niche, Location.
    """
    base_url = "https://www.yellowpages.com/search"
    params = {"search_terms": niche, "geo_location_terms": location}
    search_url = f"{base_url}?{urlencode(params)}"

    session = requests.Session()
    session.headers.update(HEADERS)

    leads: list[dict] = []
    page = 1

    while len(leads) < max_results:
        url = f"{search_url}&page={page}"
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"[Scraper] HTTP error on page {page}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"[Scraper] Request failed on page {page}: {e}")
            break

        soup = BeautifulSoup(response.content, "lxml")
        listings = soup.select("div.organic div.result")
        if not listings:
            listings = soup.select("div.result")

        if not listings:
            print(f"[Scraper] No listings found on page {page}.")
            break

        for listing in listings:
            if len(leads) >= max_results:
                break
            lead = _parse_listing(listing, niche, location)
            if lead["Business Name"] != "N/A":
                leads.append(lead)

        if not soup.select_one("a.next"):
            break

        page += 1
        time.sleep(random.uniform(1.5, 3.5))

    return leads


def _parse_listing(listing, niche: str, location: str) -> dict:
    """Parse a single Yellow Pages listing into a lead dict."""

    def text(selector: str) -> str:
        tag = listing.select_one(selector)
        return tag.get_text(strip=True) if tag else "N/A"

    name    = text(".business-name span")
    phone   = text(".phones.phone.primary")
    street  = text(".street-address")
    city    = text(".locality")
    address = f"{street}, {city}" if street != "N/A" and city != "N/A" else (street if street != "N/A" else city)

    website_tag = listing.select_one("a.track-visit-website")
    website = website_tag["href"] if website_tag and website_tag.get("href") else "N/A"

    rating_tag = listing.select_one("div.result-rating")
    if rating_tag:
        classes = rating_tag.get("class", [])
        rating_class = next((c for c in classes if c.startswith("rating-")), None)
        rating = rating_class.replace("rating-", "").replace("-", ".") if rating_class else "N/A"
    else:
        rating = "N/A"

    review_tag   = listing.select_one("a.count")
    review_count = review_tag.get_text(strip=True).strip("()") if review_tag else "0"

    cat_tags   = listing.select(".categories a")
    categories = ", ".join(c.get_text(strip=True) for c in cat_tags) if cat_tags else niche

    years_tag = listing.select_one(".years-in-business .count")
    years     = years_tag.get_text(strip=True) if years_tag else "N/A"

    return {
        "Business Name": name, "Phone": phone, "Address": address,
        "Website": website,    "Email": "N/A", "Rating": rating,
        "Review Count": review_count, "Years in Biz": years,
        "Category": categories, "Niche": niche, "Location": location,
    }
