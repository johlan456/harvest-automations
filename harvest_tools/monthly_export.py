"""Export Tracks 4 Africa time entries from Harvest to XLSX for the current month."""

from datetime import date, datetime, timedelta, timezone

from openpyxl import Workbook
from openpyxl.styles import Font

from .client import get_client
from .telegram import send_document, send_message

PROJECT_ID = 47325879  # HEV004 — System Admin Services
TASK_ID = 26287739  # Tracks 4 Africa
CALENDAR_NAME = "T4A"


def _month_range(ref_date: date) -> tuple[date, date]:
    """Return first and last day of the month containing ref_date."""
    first = ref_date.replace(day=1)
    # Last day: go to next month's 1st, subtract a day
    if first.month == 12:
        last = first.replace(year=first.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last = first.replace(month=first.month + 1, day=1) - timedelta(days=1)
    return first, last


def _fetch_entries(start: date, end: date) -> list[dict]:
    """Fetch all T4A time entries in the date range, handling pagination."""
    client = get_client()
    entries = []
    page = 1
    while True:
        resp = client.get(
            "/time_entries",
            params={
                "project_id": PROJECT_ID,
                "task_id": TASK_ID,
                "from": str(start),
                "to": str(end),
                "per_page": 100,
                "page": page,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        entries.extend(data["time_entries"])
        if page >= data["total_pages"]:
            break
        page += 1
    return entries


def _hours_to_time_str(hours: float) -> str:
    """Convert decimal hours to HH:MM string."""
    total_minutes = round(hours * 60)
    h, m = divmod(total_minutes, 60)
    return f"{h}:{m:02d}"


def _parse_start_time(entry: dict) -> datetime | None:
    """Get start time from started_time (timer) or created_at (fallback)."""
    spent = date.fromisoformat(entry["spent_date"])
    if entry.get("started_time"):
        t = datetime.strptime(entry["started_time"], "%I:%M%p").time()
        return datetime.combine(spent, t)
    if entry.get("created_at"):
        sast = timezone(timedelta(hours=2))
        utc_dt = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
        return utc_dt.astimezone(sast).replace(tzinfo=None)
    return None


def _fmt_dt(dt: datetime | None) -> str | None:
    """Format a datetime as 'DD/MM/YYYY HH:MM', or None."""
    if dt is None:
        return None
    return dt.strftime("%d/%m/%Y %H:%M")


def _build_workbook(entries: list[dict]) -> Workbook:
    """Build an XLSX workbook matching the T4A report template."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    headers = [
        "Calendar Name",
        "Event Title",
        "Start Date/Time",
        "End Date/Time",
        "Duration (Hours, per 15 minutes commenced)",
        "Event Notes",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    total_seconds = 0
    for e in entries:
        hours = e["hours"]
        notes = (e.get("notes") or "").strip()
        start = _parse_start_time(e)
        end = start + timedelta(hours=hours) if start else None

        ws.append([
            CALENDAR_NAME,
            notes,
            _fmt_dt(start),
            _fmt_dt(end),
            _hours_to_time_str(hours),
            "",  # Event Notes — left empty
        ])
        total_seconds += round(hours * 3600)

    # Total row in the Duration column
    total_row = ws.max_row + 1
    total_h, remainder = divmod(total_seconds, 3600)
    total_m = remainder // 60
    ws.cell(row=total_row, column=5, value=f"{total_h}:{total_m:02d}")

    return wb


def main():
    today = date.today()
    start, end = _month_range(today)
    print(f"Fetching T4A entries for {start.strftime('%B %Y')}...")

    entries = _fetch_entries(start, end)

    if not entries:
        msg = f"T4A Export — {start.strftime('%B %Y')}: No Tracks 4 Africa entries found for this month."
        print(msg)
        send_message(msg)
        return

    wb = _build_workbook(entries)
    filename = f"tracks4africa-{today.strftime('%Y-%m')}.xlsx"
    wb.save(filename)
    print(f"Exported {len(entries)} entries to {filename}")

    caption = f"T4A Export — {start.strftime('%B %Y')}"
    send_document(filename, caption=caption)
    print("Sent to Telegram.")


if __name__ == "__main__":
    main()
