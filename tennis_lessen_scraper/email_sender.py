"""Verstuur Excel-lijst per e-mail."""

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
SMTP_PORT = 465  # SSL (587 wordt soms geblokkeerd vanuit datacenters)
SMTP_USER = "leemanskoen1978@gmail.com"


def send_lessen_email() -> bool:
    """Verstuur het Excel-bestand per e-mail naar EMAIL_TO."""
    password = load_email_credentials()
    if not password and not IS_CI:
        try:
            password = getpass.getpass("Voer Gmail wachtwoord in (leemanskoen1978@gmail.com): ")
            if password:
                save_email_credentials(password)
                print("E-mail wachtwoord opgeslagen voor volgende keren.")
        except EOFError:
            password = None
    if not password:
        logger.warning("Geen e-mail wachtwoord (lokaal: wordt gevraagd bij verzenden).")
        return False

    path = Path(EXCEL_OUTPUT)
    if not path.exists():
        logger.error("Excel-bestand niet gevonden: %s", path)
        return False

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

    try:
        with open(path, "rb") as f:
            part = MIMEBase("application", "vnd.ms-excel")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{path.name}"',
        )
        msg.attach(part)

        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, password)
                server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, password)
                server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
        logger.info("E-mail verstuurd naar %s", EMAIL_TO)
        return True
    except Exception as e:
        logger.exception("E-mail verzenden mislukt: %s", e)
        return False
