#!/usr/bin/env python3
"""
Sla alle credentials op voor de tennis scraper.
Run eenmalig; daarna hoeft u niets meer in te voeren.
"""

import getpass
import sys
from pathlib import Path

# Zorg dat tennis_lessen_scraper importeerbaar is
sys.path.insert(0, str(Path(__file__).parent))

from tennis_lessen_scraper.credentials import (
    save_credentials,
    save_email_credentials,
)
from tennis_lessen_scraper.config import BASE_DIR

ENV_FILE = BASE_DIR.parent / ".env"


def main():
    print("=" * 55)
    print("Tennis scraper – alle credentials opslaan")
    print("=" * 55)
    print()

    # 1. Tennis Vlaanderen
    print("1. Tennis Vlaanderen (tennisenpadelvlaanderen.be)")
    print("-" * 40)
    tennis_user = input("Lidnummer of e-mailadres: ").strip()
    tennis_pass = getpass.getpass("Wachtwoord: ")
    if tennis_user and tennis_pass:
        save_credentials(tennis_user, tennis_pass)
        print("   ✓ Opgeslagen (versleuteld)")
    else:
        print("   ✗ Overgeslagen (lege velden)")
    print()

    # 2. Gmail (voor verzenden)
    print("2. Gmail (leemanskoen1978@gmail.com)")
    print("-" * 40)
    print("   Gebruik app-wachtwoord als je 2FA hebt.")
    gmail_pass = getpass.getpass("Gmail wachtwoord: ")
    if gmail_pass:
        save_email_credentials(gmail_pass)
        print("   ✓ Opgeslagen (versleuteld)")
    else:
        print("   ✗ Overgeslagen")
    print()

    # 3. Google Calendar
    print("3. Google Calendar (voor privé lessen)")
    print("-" * 40)
    client_id = input("GOOGLE_CLIENT_ID: ").strip()
    client_secret = input("GOOGLE_CLIENT_SECRET: ").strip()
    refresh_token = input("GOOGLE_REFRESH_TOKEN: ").strip()
    if client_id and client_secret and refresh_token:
        content = (
            f"GOOGLE_CLIENT_ID=\"{client_id}\"\n"
            f"GOOGLE_CLIENT_SECRET=\"{client_secret}\"\n"
            f"GOOGLE_REFRESH_TOKEN=\"{refresh_token}\"\n"
        )
        ENV_FILE.write_text(content)
        ENV_FILE.chmod(0o600)
        print("   ✓ Opgeslagen in .env")
    else:
        print("   ✗ Overgeslagen (alle 3 velden nodig)")
    print()

    print("=" * 55)
    print("Klaar. Run nu: python run_tennis_scraper.py --scrape")
    print("=" * 55)
    return 0


if __name__ == "__main__":
    sys.exit(main())
