"""Configuratie voor de Tennis en Padel Vlaanderen lessen scraper."""

import os
import tempfile
from pathlib import Path

# Bestanden
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.enc"
SESSION_STATE_FILE = BASE_DIR / "browser_session.json"

# Cloud/CI mode (GitHub Actions): gebruik temp bestand
IS_CI = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
EXCEL_OUTPUT = (
    Path(tempfile.gettempdir()) / "tennis_lessen.xlsx"
    if IS_CI
    else Path("/Users/leko/Documents/Python/origineel factuur.xlsm")
)
SHEET_NAME = "lessen_data"

# Website
BASE_URL = "https://www.tennisenpadelvlaanderen.be"
LOGIN_URL = f"{BASE_URL}/login"
LESSEN_URL = f"{BASE_URL}/nl/academy-opvolging-lessen"
TRAINER_ID = "639541"
STATUS_ID = "5"  # Afgewerkte lessen (pas aan indien nodig)
SEARCH_TYPE = "lessen"

# Kolommen voor Excel (exacte volgorde)
COLUMNS = [
    "Club",
    "Aanbod",
    "Doelgroep",
    "Groep",
    "Dag + uur",
    "Trainer",
    "Aanwezigh.",
    "Uur/locatie gewijzigd?",
    "Status",
    "Bedrag",
]

# Encryptie key - wordt gegenereerd bij eerste run (lokaal opgeslagen)
# Voor extra beveiliging: gebruik environment variable
SECRET_KEY = os.environ.get("TENNIS_SCRAPER_SECRET", "tennis-padel-vlaanderen-2026")

# E-mail
EMAIL_TO = "leemanskoen1978@gmail.com"
EMAIL_CREDENTIALS_FILE = BASE_DIR / "email_credentials.enc"
