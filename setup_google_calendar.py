#!/usr/bin/env python3
"""
Eenmalig: haal Google Calendar OAuth-credentials op.
Opent je browser voor inloggen; daarna krijg je de waarden om in te stellen.
"""

import os
import sys

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",  # Voor e-mail verzenden via API (geen SMTP)
]

def main():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Installeer eerst: pip install google-auth-oauthlib")
        return 1

    print("=" * 60)
    print("Google Calendar API – credentials ophalen")
    print("=" * 60)
    print()
    print("Stap 1: Ga naar https://console.cloud.google.com/")
    print("  - Maak een project (of kies bestaand)")
    print("  - Zoek 'Google Calendar API' en schakel in")
    print("  - Zoek 'Gmail API' en schakel ook in (voor e-mail versturen)")
    print("  - Ga naar APIs & Services → Credentials")
    print("  - Create Credentials → OAuth client ID")
    print("  - App type: Desktop app")
    print("  - Download de JSON (rechter muisknop op de client → Download)")
    print()
    print("Stap 2: Sla het bestand op als: client_secret.json")
    print("        in deze map: Webscraping/")
    print()

    secret_path = os.path.join(os.path.dirname(__file__), "client_secret.json")
    if not os.path.exists(secret_path):
        print("client_secret.json niet gevonden.")
        print("Plaats het gedownloade bestand in:", os.path.dirname(os.path.abspath(secret_path)))
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
    creds = flow.run_local_server(port=0)

    refresh = getattr(creds, "refresh_token", None)
    with open(secret_path) as f:
        import json
        data = json.load(f)
        client_id = data.get("installed", data.get("web", {})).get("client_id", "")
        client_secret = data.get("installed", data.get("web", {})).get("client_secret", "")

    print()
    print("=" * 60)
    print("Gebruik deze waarden (lokaal of in GitHub Secrets):")
    print("=" * 60)
    print()
    print("GOOGLE_CLIENT_ID=" + repr(client_id))
    print("GOOGLE_CLIENT_SECRET=" + repr(client_secret))
    print("GOOGLE_REFRESH_TOKEN=" + repr(refresh))
    print()
    print("Lokaal – voer uit vóór de scrape:")
    print('  export GOOGLE_CLIENT_ID="' + client_id + '"')
    print('  export GOOGLE_CLIENT_SECRET="' + client_secret + '"')
    print('  export GOOGLE_REFRESH_TOKEN="' + refresh + '"')
    print()
    print("Of maak een bestand .env in Webscraping/ met deze regels,")
    print("en run: source .env  (of gebruik python-dotenv)")
    print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
