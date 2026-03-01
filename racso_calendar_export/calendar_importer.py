#!/usr/bin/env python3
"""
macOS Calendar racso-export: volledig automatisch.
- Kalender: Family
- Periode: vorige kalendermaand (1e t/m laatste dag)
- Export: altijd .xls in de map van dit script
Gebruik met launchd voor 1e van elke maand om 07:00.
"""

import subprocess
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

(calendar_name, chunk_start, chunk_end, timeout_seconds=90):
    """Haal alle events op voor een kort datumbereik (één chunk). Geen racso-filter in script."""
    start_str = chunk_start.strftime('%m/%d/%Y %H:%M')
    end_str = chunk_end.strftime('%m/%d/%Y %H:%M')
    cal_escaped = calendar_name.replace('\\', '\\\\').replace('"', '\\"')
    script = f'''
    tell application "Calendar"
        set targetCalendar to calendar "{cal_escaped}"
        set outEvents to {{}}
        set startDate to date "{start_str}"
        set endDate to date "{end_str}"
        set rangeEvents to (every event of targetCalendar where (its start date ≥ startDate and its end date ≤ endDate))
        repeat with anEvent in rangeEvents
            set eventSummary to summary of anEvent
            set eventStart to start date of anEvent
            set eventEnd to end date of anEvent
            set eventLocation to ""
            set eventDescription to ""
            try
                set eventLocation to location of anEvent
            end try
            try
                set eventDescription to description of anEvent
            end try
            set startISO to my dateToISO(eventStart)
            set endISO to my dateToISO(eventEnd)
            set eventInfo to eventSummary & "|||" & startISO & "|||" & endISO & "|||" & eventLocation & "|||" & eventDescription
            set end of outEvents to eventInfo
        end repeat
        return outEvents
    end tell
    on dateToISO(theDate)
        set y to year of theDate as string
        set m to month of theDate as integer
        set d to day of theDate as integer
        set h to hours of theDate as integer
        set min to minutes of theDate as integer
        if m < 10 then set m to "0" & m
        if d < 10 then set d to "0" & d
        if h < 10 then set h to "0" & h
        if min < 10 then set min to "0" & min
        return y & "-" & m & "-" & d & " " & h & ":" & min
    end dateToISO
    '''
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=True,
    )
    events = []
    output = (result.stdout or '').strip()
    if output:
        for event_str in output.split(', '):
            if '|||' not in event_str:
                continue
            parts = event_str.split('|||')
            if len(parts) >= 3:
                events.append({
                    'summary': parts[0].strip(),
                    'start': parts[1].strip(),
                    'end': parts[2].strip(),
                    'location': parts[3].strip() if len(parts) > 3 else '',
                    'description': parts[4].strip() if len(parts) > 4 else '',
                })
    return events


def get_events_with_racso(calendar_name, start_date, end_date):
    """Get events that contain 'racso' in the name within date range.
    Chunks the range by month to avoid AppleEvent timeout; filters racso in Python.
    """
    # Chunks van één maand om timeout te voorkomen
    chunks = []
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    while current <= end:
        # Einde van deze maand
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1, day=1)
        else:
            next_month = current.replace(month=current.month + 1, day=1)
        chunk_end = next_month - timedelta(seconds=1)
        if chunk_end > end:
            chunk_end = end
        chunk_start = current
        chunks.append((chunk_start, chunk_end))
        current = next_month

    all_events = []
    for i, (chunk_start, chunk_end) in enumerate(chunks):
        try:
            chunk_events = _get_events_in_range_chunk(
                calendar_name, chunk_start, chunk_end, timeout_seconds=90
            )
            # Alleen events met 'racso' in de titel
            for e in chunk_events:
                if 'racso' in (e.get('summary') or '').lower():
                    all_events.append(e)
        except subprocess.TimeoutExpired:
            print(f"  Waarschuwing: timeout voor chunk {chunk_start.date()} - {chunk_end.date()}, overgeslagen.")
        except subprocess.CalledProcessError as e:
            print(f"  Fout bij chunk {chunk_start.date()} - {chunk_end.date()}: {e.stderr or e}")

    all_events.sort(key=lambda x: x['start'])
    return all_events


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
