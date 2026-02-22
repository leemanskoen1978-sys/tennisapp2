"""Datumbereik voor de vorige maand."""

from datetime import date
from calendar import monthrange


def get_previous_month_range() -> tuple[str, str]:
    """
    Geef start- en einddatum van de vorige maand terug.
    Returns: (start_date, end_date) als DD-MM-YYYY strings
    """
    today = date.today()
    if today.month == 1:
        prev_month = 12
        prev_year = today.year - 1
    else:
        prev_month = today.month - 1
        prev_year = today.year

    _, last_day = monthrange(prev_year, prev_month)
    start_date = date(prev_year, prev_month, 1)
    end_date = date(prev_year, prev_month, last_day)

    return (
        start_date.strftime("%d-%m-%Y"),
        end_date.strftime("%d-%m-%Y"),
    )
