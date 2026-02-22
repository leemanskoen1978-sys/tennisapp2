"""Scraper voor Tennis en Padel Vlaanderen lessen met Playwright."""

import logging
import time

from playwright.sync_api import sync_playwright, Page

from .config import (
    LOGIN_URL,
    LESSEN_URL,
    TRAINER_ID,
    STATUS_ID,
    SEARCH_TYPE,
    SESSION_STATE_FILE,
    COLUMNS,
)
from .credentials import load_credentials
from .dates import get_previous_month_range

logger = logging.getLogger(__name__)


def _accept_cookies_if_needed(page: Page) -> None:
    """Accepteer cookie-banner indien aanwezig."""
    try:
        selectors = [
            'button:has-text("Alle cookies accepteren")',
            'button:has-text("Accepteren")',
            'a:has-text("Alle cookies accepteren")',
            '[data-testid="accept-cookies"]',
            '#onetrust-accept-btn-handler',
        ]
        for sel in selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(1)
                    return
            except Exception:
                continue
    except Exception as e:
        logger.debug("Cookie-banner niet gevonden: %s", e)


def _do_login(page: Page, username: str, password: str) -> bool:
    """Voer login uit."""
    try:
        page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        _accept_cookies_if_needed(page)

        email_selectors = [
            'input[name="login"]',
            'input[placeholder*="Lidnummer"]',
            'input[placeholder*="e-mail"]',
            'input[type="email"]',
            '#_com_liferay_login_web_portlet_LoginPortlet_login',
            'input[id*="login"]',
        ]
        email_filled = False
        for sel in email_selectors:
            try:
                page.locator(sel).first.fill(username, timeout=3000)
                email_filled = True
                break
            except Exception:
                continue

        if not email_filled:
            page.get_by_label("Lidnummer of e-mailadres").fill(username)

        page.get_by_label("Wachtwoord").fill(password)
        page.get_by_role("button", name="Inloggen").click()
        time.sleep(3)

        if "login" in page.url.lower() and "dashboard" not in page.url.lower():
            if page.locator('text="Authenticatie mislukt"').count() > 0:
                logger.error("Login mislukt - controleer credentials")
                return False
        return True
    except Exception as e:
        logger.exception("Login fout: %s", e)
        return False


def _map_row_to_columns(row_cells: list[str], headers: list[str]) -> dict[str, str]:
    """Map tabelcellen naar onze kolomstructuur."""
    result = {col: "" for col in COLUMNS}
    mapping = {
        0: "Club",
        1: "Aanbod",
        2: "Doelgroep",
        3: "Groep",
        4: "Dag + uur",
        5: "Trainer",
        6: "Aanwezigh.",
        7: "Uur/locatie gewijzigd?",
        8: "Status",
        9: "Bedrag",
    }
    for i, cell in enumerate(row_cells):
        if i in mapping and i < len(row_cells):
            val = cell.strip() if cell else ""
            result[mapping[i]] = val
    return result


def _parse_table(page: Page) -> list[dict[str, str]]:
    """Haal alle rijen uit de lessen-tabel."""
    lessons = []
    try:
        table_selectors = [
            "table.results-table",
            "table.data-table",
            "table",
            ".table-responsive table",
            "#hash_results table",
            "[role='table']",
        ]

        table = None
        for sel in table_selectors:
            try:
                table = page.locator(sel).first
                table.wait_for(state="visible", timeout=5000)
                break
            except Exception:
                continue

        if table is None:
            logger.warning("Geen tabel gevonden - controleer of je ingelogd bent")
            return lessons

        headers = []
        header_row = table.locator("thead tr, tr:first-child").first
        if header_row.count and header_row.locator("th, td").count() > 0:
            header_cells = header_row.locator("th, td").all_inner_texts()
            headers = [h.strip() for h in header_cells]

        rows = table.locator("tbody tr, tr").all()
        start_idx = 1 if headers else 0

        for row_el in rows[start_idx:]:
            try:
                cells = row_el.locator("td").all_inner_texts()
                if not cells:
                    continue
                row_data = _map_row_to_columns(cells, headers)
                if row_data.get("Club") or row_data.get("Aanbod") or len(cells) >= 5:
                    lessons.append(row_data)
            except Exception as e:
                logger.debug("Rij overslaan: %s", e)

        next_btn = page.locator('a:has-text("›"), button:has-text("Volgende"), .pagination-next')
        while next_btn.count() > 0:
            try:
                next_btn.first.click()
                time.sleep(2)
                table = page.locator("table").first
                rows = table.locator("tbody tr, tr").all()
                for row_el in rows:
                    cells = row_el.locator("td").all_inner_texts()
                    if cells:
                        lessons.append(_map_row_to_columns(cells, headers))
                next_btn = page.locator('a:has-text("›"), button:has-text("Volgende")')
                if not next_btn.first.is_visible():
                    break
            except Exception:
                break

    except Exception as e:
        logger.exception("Fout bij parsen tabel: %s", e)

    return lessons


def scrape_lessen(
    headless: bool = True,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, str]]:
    """Scrape lessen van Tennis en Padel Vlaanderen."""
    creds = load_credentials()
    if not creds:
        raise ValueError(
            "Geen opgeslagen inloggegevens. Run eerst met --setup om in te loggen."
        )

    username, password = creds

    if not start_date or not end_date:
        start_date, end_date = get_previous_month_range()

    url = (
        f"{LESSEN_URL}?trainerId={TRAINER_ID}&startDate={start_date}&endDate={end_date}"
        f"&statusId={STATUS_ID}&searchType={SEARCH_TYPE}#hash_results"
    )

    lessons = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )

        if SESSION_STATE_FILE.exists():
            try:
                context = browser.new_context(storage_state=str(SESSION_STATE_FILE))
            except Exception:
                pass

        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            if "login" in page.url.lower():
                _accept_cookies_if_needed(page)
                if not _do_login(page, username, password):
                    return []
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(3)

            context.storage_state(path=str(SESSION_STATE_FILE))

            lessons = _parse_table(page)
            logger.info("Gescrapt: %d lessen", len(lessons))

        finally:
            browser.close()

    return lessons
