#!/usr/bin/env python3
"""Tennis en Padel Vlaanderen - Lessen Scraper."""

import argparse
import getpass
import logging
import sys
from pathlib import Path

from .credentials import (
    save_credentials,
    load_credentials,
    credentials_exist,
    delete_credentials,
    load_email_credentials,
    delete_email_credentials,
)
from .scraper import scrape_lessen
from .excel_export import append_lessen_to_excel, append_private_lessen_to_excel
from .email_sender import send_lessen_email
from .calendar_scraper import get_private_lessons
from .dates import get_previous_month_range
from .config import EXCEL_OUTPUT

LOG_FILE = Path(__file__).parent / "tennis_scraper.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def cmd_setup():
    """Eerste keer: vraag inloggegevens en bewaar veilig."""
    print("=" * 50)
    print("Tennis en Padel Vlaanderen - Inloggegevens opgeven")
    print("=" * 50)
    username = input("Lidnummer of e-mailadres: ").strip()
    password = getpass.getpass("Wachtwoord: ")
    if not username or not password:
        print("Fout: beide velden zijn verplicht.")
        return 1
    save_credentials(username, password)
    print("\nInloggegevens zijn veilig opgeslagen (versleuteld).")
    return 0




def cmd_scrape(
    headless: bool = True,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Scrape lessen en exporteer naar Excel."""
    if not credentials_exist():
        print("Run eerst: python run_tennis_scraper.py --setup")
        return 1

    if not start_date or not end_date:
        start_date, end_date = get_previous_month_range()
    print(f"Scrapen lessen van {start_date} t/m {end_date}...")

    try:
        # Haal lessen van website (Tennis Vlaanderen)
        website_lessen = scrape_lessen(headless=headless, start_date=start_date, end_date=end_date)
        website_added = append_lessen_to_excel(website_lessen)
        print(f"Website lessen: {len(website_lessen)} gevonden, {website_added} toegevoegd")

        # Haal privé lessen uit Google Calendar
        print(f"Haal privé lessen uit Google Calendar...")
        try:
            private_lessen = get_private_lessons()
            private_added = append_private_lessen_to_excel(private_lessen)
            print(f"Privé lessen: {len(private_lessen)} gevonden, {private_added} toegevoegd")
        except Exception as gce:
            logger.warning("Google Calendar kon niet worden gelezen: %s", gce)
            private_lessen = []
            private_added = 0
            print("Google Calendar kon niet worden gelezen (mogelijk geen connectie/credentials)")

        total_added = website_added + private_added
        print(f"Totaal toegevoegd aan Excel: {total_added} lessen (website + privé)")
        print(f"Bestand: {EXCEL_OUTPUT}")

        if send_lessen_email():
            print("E-mail verstuurd naar leemanskoen1978@gmail.com")
        else:
            print("E-mail kon niet worden verzonden (zie log).")

        return 0
    except Exception as e:
        logger.exception("Fout: %s", e)
        print(f"Fout: {e}")
        return 1


def cmd_scheduler():
    """Wordt aangeroepen door cron op de 1e van de maand."""
    return cmd_scrape(headless=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tennis Vlaanderen lessen scraper")
    parser.add_argument("--setup", action="store_true", help="Eerste keer: vul inloggegevens in")
    parser.add_argument("--scrape", action="store_true", help="Scrape lessen nu (vorige maand)")
    parser.add_argument("--visible", action="store_true", help="Toon browser tijdens scrape")
    parser.add_argument("--cron", action="store_true", help="Automatische run (1e van maand)")
    parser.add_argument("--clear-credentials", action="store_true", help="Verwijder opgeslagen inloggegevens")
    parser.add_argument("--clear-email", action="store_true", help="Verwijder opgeslagen e-mail wachtwoord")

    args = parser.parse_args()

    if args.setup:
        sys.exit(cmd_setup())
    if args.clear_credentials:
        delete_credentials()
        print("Inloggegevens verwijderd.")
        sys.exit(0)
    if args.clear_email:
        if delete_email_credentials():
            print("Opgeslagen e-mail wachtwoord verwijderd. Bij volgende scrape wordt om je Gmail wachtwoord gevraagd.")
        else:
            print("Geen opgeslagen e-mail wachtwoord gevonden.")
        sys.exit(0)
    if args.cron:
        sys.exit(cmd_scheduler())
    if args.scrape:
        sys.exit(cmd_scrape(headless=not args.visible))

    parser.print_help()
    print("\n--- Quick start ---")
    print("1. python run_tennis_scraper.py --setup")
    print("2. python run_tennis_scraper.py --scrape")
    print("3. python run_tennis_scraper.py --scrape --visible")
