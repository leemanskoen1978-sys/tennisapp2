"""Google Calendar scraper voor privé lessen."""

import logging
from datetime import datetime, timezone
from typing import Any

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    logging.error("Google Calendar bibliotheken niet gevonden. Installeer: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    raise

from .calendar_config import SESSIONS_CALENDAR_ID, PRIVATE_LESSONS_COLUMNS
from .dates import get_previous_month_range

logger = logging.getLogger(__name__)


def _prompt_google_credentials() -> tuple[str, str, str]:
    """Vraag Google Calendar credentials in de terminal (niet in CI)."""
    import os
    if os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
        raise ValueError("Google Calendar credentials ontbreken. Zet GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN als GitHub Secrets.")
    try:
        client_id = input("GOOGLE_CLIENT_ID: ").strip()
        client_secret = input("GOOGLE_CLIENT_SECRET: ").strip()
        refresh_token = input("GOOGLE_REFRESH_TOKEN: ").strip()
        return (client_id, client_secret, refresh_token)
    except EOFError:
        raise ValueError("Google Calendar credentials nodig.")


def get_google_service() -> Any:
    """Configureer en retourneer Google Calendar API service."""
    from .calendar_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN

    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET
    refresh_token = GOOGLE_REFRESH_TOKEN

    if not (client_id and client_secret and refresh_token):
        print("Google Calendar credentials nodig (uit setup_google_calendar.py):")
        client_id, client_secret, refresh_token = _prompt_google_credentials()

    try:
        creds = Credentials.from_authorized_user_info(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        if not creds.valid:
            creds.refresh(Request())
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        logger.warning("Google Calendar authenticatie mislukt: %s", e)
        raise ValueError(f"Google Calendar kon niet verbinden: {e}")


def get_private_lessons() -> list[dict[str, str]]:
    """
    Haal privé lessen uit Google Calendar van de vorige maand.
    Returns: lijst van dicts met lessen volgens PRIVATE_LESSONS_COLUMNS
    """
    service = get_google_service()
    
    # Bepaal de vorige maand (1e t/m laatste dag)
    start_date_str, end_date_str = get_previous_month_range()
    
    # Converteer naar datetime objecten voor Google API
    start_date = datetime.strptime(start_date_str, "%d-%m-%Y").replace(tzinfo=timezone.utc)
    
    # Bereken de laatste dag van de vorige maand
    from calendar import monthrange
    last_day = monthrange(start_date.year, start_date.month)[1]
    end_date = start_date.replace(day=last_day).replace(hour=23, minute=59, second=59)
    
    logger.info("Haal lessen uit Google Calendar van %s t/m %s", start_date.date(), end_date.date())
    
    lessons = []
    
    try:
        events_result = service.events().list(
            calendarId=SESSIONS_CALENDAR_ID,
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        for event in events:
            try:
                # Bepaal start en eind tijd
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                
                end = event['end'].get('dateTime', event['end'].get('date'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                
                # Alleen volledige dagen/uren tellen mee
                if len(lessons) >= 999:
                    break

                lesson = {
                    "Datum": start_dt.strftime("%d-%m-%Y"),
                    "Start tijd": start_dt.strftime("%H:%M"),
                    "Eind tijd": end_dt.strftime("%H:%M"),
                    "Omschrijving": event.get('summary', 'Privé les'),
                    "Locatie": event.get('location', ''),
                    "Notities": event.get('description', '').replace('\n', ' | ').strip(),
                    "Duur (uren)": str(round((end_dt - start_dt).total_seconds() / 3600, 2)),
                    "Uurvorm": "Privé lesson",
                }
                
                lessons.append(lesson)
                
            except (KeyError, ValueError) as e:
                logger.warning("Event overslaan door fout: %s", e)
                continue
        
        logger.info("Gevonden %d privé lessen in Google Calendar", len(lessons))
        
    except HttpError as e:
        logger.error("Google Calendar API fout: %s", e)
        raise
    
    return lessons
