"""Configuratie voor Google Calendar API."""

import os

# Google Calendar – welke kalender te lezen
SESSIONS_CALENDAR_ID = "leemanskoen1978@gmail.com"

# Kolommen voor privé lessen in Excel
PRIVATE_LESSONS_COLUMNS = [
    "Datum",
    "Start tijd",
    "Eind tijd",
    "Omschrijving",
    "Locatie",
    "Notities",
    "Duur (uren)",
    "Uurvorm",
]

# Google API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN")
