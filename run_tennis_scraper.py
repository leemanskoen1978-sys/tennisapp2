#!/usr/bin/env python3
"""
Startscript voor Tennis Vlaanderen lessen scraper.
Run vanaf: Webscraping/
"""
import argparse
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

# Laad .env (vóór andere imports die GOOGLE_* nodig hebben)
_env_path = BASE / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and val and key.startswith("GOOGLE_"):
                os.environ.setdefault(key, val)

from tennis_lessen_scraper.main import cmd_setup, cmd_scrape, cmd_scheduler
from tennis_lessen_scraper.credentials import delete_credentials, delete_email_credentials

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tennis Vlaanderen lessen scraper")
    parser.add_argument("--setup", action="store_true", help="Eerste keer: vul inloggegevens in")
    parser.add_argument("--scrape", action="store_true", help="Scrape lessen nu")
    parser.add_argument("--visible", action="store_true", help="Toon browser (debug)")
    parser.add_argument("--cron", action="store_true", help="Automatische run (1e v/d maand)")
    parser.add_argument("--clear-credentials", action="store_true", help="Verwijder inloggegevens")
    parser.add_argument("--clear-email", action="store_true", help="Verwijder opgeslagen e-mail wachtwoord")
    parser.add_argument("--start-date", type=str, help="Startdatum DD-MM-YYYY")
    parser.add_argument("--end-date", type=str, help="Einddatum DD-MM-YYYY")

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
        sys.exit(cmd_scrape(
            headless=not args.visible,
            start_date=args.start_date,
            end_date=args.end_date,
        ))

    parser.print_help()
    print("\nQuick start:")
    print("  python run_tennis_scraper.py --setup")
    print("  python run_tennis_scraper.py --scrape")
    print("  python run_tennis_scraper.py --scrape --visible")
