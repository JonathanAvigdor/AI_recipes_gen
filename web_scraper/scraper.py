import os
import re
from typing import List, Tuple

# --- Cloud-friendly path: requests + BeautifulSoup ---
import requests
from bs4 import BeautifulSoup

# --- Local path: Selenium (optional) ---
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    _HAS_SELENIUM = True
except Exception:
    _HAS_SELENIUM = False

PRICE_PAT = re.compile(r"\d{1,3}(?:[.,]\d{1,2})?\s*kr", re.IGNORECASE)

def _clean_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _extract_title_and_price(text: str) -> Tuple[str, str]:
    text = _clean_space(text)
    price_match = PRICE_PAT.search(text)
    price = price_match.group(0) if price_match else ""
    title = text
    if price:
        title = (text[:price_match.start()] + text[price_match.end():]).strip(" -:;|,")
    if len(title) > 140:
        title = title[:140] + "…"
    return title, (price or "—")

# -----------------------------
# Cloud scraper (requests + bs4)
# -----------------------------
def _scrape_requests(url: str) -> List[Tuple[str, str]]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    candidates = []
    for tag in soup.find_all(["article", "li", "div"]):
        cls = " ".join(tag.get("class") or [])
        if re.search(r"(offer|product|card|grid|tile|item)", cls, re.IGNORECASE):
            txt = tag.get_text(separator=" ", strip=True)
            if PRICE_PAT.search(txt) and len(txt) > 20:
                candidates.append(txt)

    if not candidates:
        for tag in soup.find_all(string=PRICE_PAT):
            block = tag.parent.get_text(separator=" ", strip=True)
            if len(block) > 20:
                candidates.append(block)

    seen, clean = set(), []
    for c in candidates:
        c2 = _clean_space(c)
        if c2 not in seen:
            seen.add(c2)
            clean.append(c2)

    results: List[Tuple[str, str]] = []
    for c in clean:
        title, price = _extract_title_and_price(c)
        if len(re.sub(r"[^A-Za-zÅÄÖåäöÉéÜüÆæØøß]", "", title)) >= 3:
            results.append((title, price))

    return results[:60]

# -----------------------------
# Local scraper (Selenium)
# -----------------------------
def _scrape_selenium(url: str) -> List[Tuple[str, str]]:
    if not _HAS_SELENIUM:
        return []
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    try:
        driver.get(url)
        driver.implicitly_wait(5)

        texts = []
        elems = driver.find_elements(
            By.XPATH,
            "//article|//li|//div[contains(@class,'product') or contains(@class,'offer')]"
        )
        if not elems:
            elems = driver.find_elements(By.XPATH, "//*")
        for el in elems:
            try:
                txt = el.text
                if PRICE_PAT.search(txt) and len(txt) > 20:
                    texts.append(txt)
            except Exception:
                pass

        seen, blocks = set(), []
        for t in texts:
            t2 = _clean_space(t)
            if t2 not in seen:
                seen.add(t2)
                blocks.append(t2)

        results = []
        for b in blocks:
            title, price = _extract_title_and_price(b)
            if len(title) >= 3:
                results.append((title, price))
        return results[:60]
    finally:
        driver.quit()

# -----------------------------
# Public API (hybrid)
# -----------------------------
def scrape_ica_offers(url: str) -> List[Tuple[str, str]]:
    """
    Hybrid scraper:
      - If RUN_ENV=cloud -> requests+bs4 (Streamlit Cloud safe)
      - Else try Selenium first, then fallback to requests+bs4
    """
    run_env = os.getenv("RUN_ENV", "").lower()

    if run_env == "cloud":
        return _scrape_requests(url)

    try:
        data = _scrape_selenium(url)
        if data:
            return data
    except Exception:
        pass

    return _scrape_requests(url)
