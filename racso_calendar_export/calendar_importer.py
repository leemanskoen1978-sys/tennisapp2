#!/usr/bin/env python3
"""
macOS Calendar racso-export: volledig automatisch.
- Kalender: Family
- Periode: vorige kalendermaand (1e t/m laatste dag)
- Export: altijd .xls in de map van dit script
Gebruik met launchd voor 1e van elke maand om 07:00.
Gebruikt EventKit (geen AppleScript) om AppleEvent-timeouts te vermijden.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import xlwt

# Kalender en export zijn vast
CALENDAR_NAME = "Family"
OUTPUT_DIR = Path(__file__).resolve().parent  # .xls in dezelfde map als dit script

# Titels die niet geëxporteerd mogen worden
EXCLUDE_TITLE = "Tennis afspraken (Koen Leemans)"
MAX_BLOCK_HOURS = 2


def _get_events_via_eventkit(calendar_name, start_date, end_date):
    """Haal events op via EventKit (directe Calendar API, geen AppleScript/timeout)."""
    from EventKit import EKEventStore
    from Foundation import NSDate

    def _dt_to_ns(dt):
        return NSDate.dateWithTimeIntervalSince1970_(dt.timestamp())

    store = EKEventStore()

    # Permission (async) – nodig voor toegang tot events
    import threading
    done = threading.Event()
    granted = [None]

    def completion(given, err):
        granted[0] = given
        done.set()

    store.requestFullAccessToEventsWithCompletion_(completion)
    if not done.wait(timeout=30):
        raise RuntimeError("Geen antwoord op Calendar-toegang.")
    if not granted[0]:
        raise RuntimeError("Geen toegang tot Calendar. Ga naar Systeemvoorkeuren > Privacy > Kalenders.")

    # Zoek kalender op naam
    calendars = store.calendarsForEntityType_(0)  # 0 = EKEntityTypeEvent
    cal = None
    for c in (calendars or []):
        if (c.title() or "").strip() == calendar_name:
            cal = c
            break
    if not cal:
        raise RuntimeError(f"Kalender '{calendar_name}' niet gevonden.")

    # Events in bereik ophalen
    start_ns = _dt_to_ns(start_date)
    end_ns = _dt_to_ns(end_date)
    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(
        start_ns, end_ns, [cal]
    )
    ek_events = store.eventsMatchingPredicate_(predicate)
    if not ek_events:
        return []

    events = []
    for ev in ek_events:
        title = (ev.title() or "").strip()
        if "racso" not in title.lower():
            continue
        start_ns = ev.startDate()
        end_ns = ev.endDate()
        start_ts = start_ns.timeIntervalSince1970() if start_ns else 0
        end_ts = end_ns.timeIntervalSince1970() if end_ns else 0
        start_str = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M")
        end_str = datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M")
        loc = (ev.location() or "").strip()
        notes = (ev.notes() or "").strip()
        events.append({
            "summary": title,
            "start": start_str,
            "end": end_str,
            "location": loc,
            "description": notes,
        })
    return events


def get_date_range():
    """Altijd vorige kalendermaand: eerste dag 00:00 t/m laatste dag 23:59."""
    from datetime import date
    import calendar as cal_mod

    today = date.today()
    if today.month == 1:
        first = date(today.year - 1, 12, 1)
        last = date(today.year - 1, 12, cal_mod.monthrange(today.year - 1, 12)[1])
    else:
        first = date(today.year, today.month - 1, 1)
        last = date(today.year, today.month - 1, cal_mod.monthrange(today.year, today.month - 1)[1])

    start_date = datetime.combine(first, datetime.min.time())
    end_date = datetime.combine(last, datetime.max.time()).replace(microsecond=999999)
    return start_date, end_date


def get_events_with_racso(calendar_name, start_date, end_date):
    """Haal events met 'racso' op via EventKit (geen AppleScript)."""
    events = _get_events_via_eventkit(calendar_name, start_date, end_date)
    events.sort(key=lambda x: x["start"])
    return events


def _parse_event_datetime(s):
    """Parse event start/end string 'YYYY-MM-DD HH:MM' to datetime."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s[:16], "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def filter_events_for_export(events):
    """
    Filter events voor maandelijkse export:
    - Sluit 'Tennis afspraken (Koen Leemans)' uit
    - Sluit blokken > 2u met dezelfde naam uit
    - Maximaal 1 event per uur per dag; bij meerdere: voorkeur voor degene met 'racso' in de titel
    """
    if not events:
        return []

    def has_racso(summary):
        return "racso" in (summary or "").lower()

    # 1) Tennis afspraken (Koen Leemans) uitsluiten
    events = [e for e in events if EXCLUDE_TITLE not in (e.get("summary") or "")]

    # 2) Parse start/end en sluit blokken > 2u uit
    with_dt = []
    for e in events:
        start_dt = _parse_event_datetime(e.get("start"))
        end_dt = _parse_event_datetime(e.get("end"))
        if not start_dt or not end_dt:
            continue
        duration_h = (end_dt - start_dt).total_seconds() / 3600
        if duration_h > MAX_BLOCK_HOURS:
            continue
        with_dt.append((e, start_dt))

    # 3) Sorteer: eerst op datum+uur, dan racso eerst (has_racso=True vóór False)
    with_dt.sort(key=lambda t: (t[1].date(), t[1].hour, not has_racso(t[0].get("summary") or "")))

    # 4) Eén event per (dag, uur) – eerste na sortering is de gewenste (racso heeft voorkeur)
    seen = set()
    result = []
    for e, start_dt in with_dt:
        key = (start_dt.date(), start_dt.hour)
        if key in seen:
            continue
        seen.add(key)
        result.append(e)

    return result


def save_events_to_excel(events, calendar_name, start_date, end_date):
    """Save events to a legacy Excel file (.xls) in OUTPUT_DIR."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"racso_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xls"
    filepath = OUTPUT_DIR / filename

    wb = xlwt.Workbook()
    ws = wb.add_sheet("Racso Events")

    header_style = xlwt.easyxf(
        "font: bold on; align: horiz center, vert center; pattern: pattern solid, fore_colour light_blue; font: color white;"
    )
    bold_style = xlwt.easyxf("font: bold on;")
    normal_style = xlwt.easyxf("align: wrap on;")

    # Metadata
    ws.write(0, 0, f"Calendar Events Export - {calendar_name}", bold_style)
    ws.write(1, 0, f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    ws.write(2, 0, f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ws.write(3, 0, f"Total Events: {len(events)}", bold_style)

    headers = ["Event Name", "Start Date/Time", "End Date/Time", "Location", "Description"]
    for col, header in enumerate(headers):
        ws.write(5, col, header, header_style)

    for row, event in enumerate(events, 6):
        ws.write(row, 0, event.get("summary", ""), normal_style)
        ws.write(row, 1, event.get("start", ""))
        ws.write(row, 2, event.get("end", ""))
        ws.write(row, 3, event.get("location", ""), normal_style)
        ws.write(row, 4, event.get("description", ""), normal_style)

    ws.col(0).width = 30 * 256
    ws.col(1).width = 20 * 256
    ws.col(2).width = 20 * 256
    ws.col(3).width = 25 * 256
    ws.col(4).width = 40 * 256

    wb.save(str(filepath))
    return str(filepath)


def main():
    # Volledig automatisch: Family, vorige maand, altijd .xls
    start_date, end_date = get_date_range()

    events = get_events_with_racso(CALENDAR_NAME, start_date, end_date)
    events = filter_events_for_export(events)

    if not events:
        # Geen fout: gewoon geen events in die periode
        sys.exit(0)

    try:
        out_path = save_events_to_excel(events, CALENDAR_NAME, start_date, end_date)
        print(out_path)
    except Exception as e:
        print(f"Export mislukt: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
