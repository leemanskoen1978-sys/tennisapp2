#!/usr/bin/env python3
"""Vraag Google OAuth-gegevens en schrijf naar .env."""

import os

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

def main():
    print("Voer je Google OAuth-gegevens in (uit setup_google_calendar.py):")
    print()
    client_id = input("GOOGLE_CLIENT_ID: ").strip().strip("'\"")
    client_secret = input("GOOGLE_CLIENT_SECRET: ").strip().strip("'\"")
    refresh_token = input("GOOGLE_REFRESH_TOKEN: ").strip().strip("'\"")
    
    if not all([client_id, client_secret, refresh_token]):
        print("Alle drie de velden zijn verplicht. Afgebroken.")
        return 1
    
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                if line.strip().startswith(("GOOGLE_CLIENT_ID=", "GOOGLE_CLIENT_SECRET=", "GOOGLE_REFRESH_TOKEN=")):
                    continue
                lines.append(line.rstrip())
    
    lines.extend([
        f'GOOGLE_CLIENT_ID="{client_id}"',
        f'GOOGLE_CLIENT_SECRET="{client_secret}"',
        f'GOOGLE_REFRESH_TOKEN="{refresh_token}"',
    ])
    
    with open(ENV_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    
    print()
    print(f"Opgeslagen in {ENV_PATH}")
    return 0

if __name__ == "__main__":
    exit(main())
