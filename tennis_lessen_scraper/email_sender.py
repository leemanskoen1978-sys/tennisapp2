"""Verstuur Excel-lijst per e-mail."""

import base64
import getpass
import logging
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from datetime import datetime

from .config import EXCEL_OUTPUT, EMAIL_TO, IS_CI
from .credentials import load_email_credentials, save_email_credentials

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL
SMTP_USER = "leemanskoen1978@gmail.com"


def _build_message(path: Path) -> MIMEMultipart:
    """Bouw MIME-bericht met Excel-bijlage."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"Tennis lessen overzicht - {datetime.now().strftime('%d-%m-%Y')}"

    body = (
        f"Beste,\n\n"
        f"Hierbij de actuele lessenlijst uit het Tennis en Padel Vlaanderen portaal.\n\n"
        f"Met vriendelijke groeten\n"
        f"Tennis Lessen Scraper"
    )
    msg.attach(MIMEText(body, "plain"))

    with open(path, "rb") as f:
        part = MIMEBase("application", "vnd.ms-excel")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{path.name}"',
    )
    msg.attach(part)
    return msg


def _send_via_gmail_api(msg: MIMEMultipart) -> bool:
    """Verstuur via Gmail API (HTTPS) – geen SMTP, dus geen blacklist."""
    import os
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "").strip()

    if not (client_id and client_secret and refresh_token):
        logger.warning(
            "Gmail API overgeslagen: GOOGLE_CLIENT_ID/CLIENT_SECRET/REFRESH_TOKEN ontbreken "
            "(lengtes: %s/%s/%s)",
            len(client_id), len(client_secret), len(refresh_token),
        )
        return False

    logger.info("Probeer e-mail via Gmail API...")
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

        service = build("gmail", "v1", credentials=creds)
        raw = base64.urlsafe_b64encode(msg.as_string().encode()).decode()
        body = {"raw": raw}
        service.users().messages().send(userId="me", body=body).execute()
        logger.info("E-mail verstuurd via Gmail API naar %s", EMAIL_TO)
        return True
    except Exception as e:
        logger.error("Gmail API verzenden mislukt: %s", e)
        return False


def _send_via_smtp(msg: MIMEMultipart, password: str) -> bool:
    """Verstuur via SMTP (lokaal; kan geblokkeerd zijn vanuit CI)."""
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, password)
            server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
        logger.info("E-mail verstuurd via SMTP naar %s", EMAIL_TO)
        return True
    except Exception as e:
        logger.exception("SMTP verzenden mislukt: %s", e)
        return False


def send_lessen_email() -> bool:
    """Verstuur het Excel-bestand per e-mail naar EMAIL_TO.

    Gebruikt Gmail API als Google OAuth credentials beschikbaar zijn (aanbevolen in CI).
    Valt anders terug op SMTP (kan geblokkeerd zijn vanuit GitHub Actions).
    """
    path = Path(EXCEL_OUTPUT)
    if not path.exists():
        logger.error("Excel-bestand niet gevonden: %s", path)
        return False

    msg = _build_message(path)

    # 1. Probeer Gmail API (HTTPS – geen SMTP-blacklist)
    if _send_via_gmail_api(msg):
        return True

    # 2. Fallback: SMTP (vereist app-wachtwoord)
    password = load_email_credentials()
    if not password and not IS_CI:
        try:
            password = getpass.getpass("Voer Gmail app-wachtwoord in (leemanskoen1978@gmail.com): ")
            if password:
                save_email_credentials(password)
                print("E-mail wachtwoord opgeslagen voor volgende keren.")
        except EOFError:
            password = None
    if not password:
        if IS_CI:
            logger.warning(
                "Gmail API mislukt en geen EMAIL_PASSWORD. Zet GOOGLE_* secrets correct "
                "en voer setup_google_calendar.py opnieuw uit (met Gmail API scope)."
            )
        else:
            logger.warning("Geen e-mail credentials. Gebruik Google OAuth of Gmail app-wachtwoord.")
        return False

    return _send_via_smtp(msg, password)
