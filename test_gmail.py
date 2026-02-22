#!/usr/bin/env python3
"""Test of Gmail SMTP-wachtwoord werkt."""

import getpass
import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "leemanskoen1978@gmail.com"

def main():
    print("Gmail wachtwoord test")
    print("-" * 40)
    password = getpass.getpass(f"Voer wachtwoord in voor {SMTP_USER}: ")
    if not password:
        print("Geen wachtwoord ingevoerd.")
        return 1
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, password)
        print("OK: Gmail wachtwoord werkt.")
        return 0
    except smtplib.SMTPAuthenticationError as e:
        print(f"FOUT: Authenticatie mislukt - {e}")
        print("Tip: Gebruik een app-wachtwoord als je 2FA hebt:")
        print("  https://myaccount.google.com/apppasswords")
        return 1
    except Exception as e:
        print(f"FOUT: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
