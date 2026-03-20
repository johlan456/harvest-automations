"""Weekly summary of Harvest time entries, delivered via email."""

from collections import defaultdict
from datetime import date, timedelta
from html import escape

from .client import get_client
from .email import send_email
from .telegram import send_message

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_ORDER = ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]


def _get_date_range() -> tuple[date, date]:
    """Return (previous Friday, current Thursday) covering a 7-day Fri–Thu window."""
    today = date.today()
    # Thursday = weekday 3. Days since last Thursday (0 if today is Thursday).
    days_since_thu = (today.weekday() - 3) % 7
    thu = today - timedelta(days=days_since_thu)
    fri = thu - timedelta(days=6)
    return fri, thu


def _fetch_entries(start: date, end: date) -> list[dict]:
    """Fetch all time entries in the date range, handling pagination."""
    client = get_client()
    entries = []
    page = 1
    while True:
        resp = client.get(
            "/time_entries",
            params={"from": str(start), "to": str(end), "per_page": 100, "page": page},
        )
        resp.raise_for_status()
        data = resp.json()
        entries.extend(data["time_entries"])
        if page >= data["total_pages"]:
            break
        page += 1
    return entries


def _group_entries(entries: list[dict]) -> dict:
    """Group entries into {project: {task: {day: [(notes, hours)]}}}."""
    projects: dict[str, dict[str, dict[str, list[tuple[str, float]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for e in entries:
        project = e["project"]["name"]
        task = e["task"]["name"]
        entry_date = date.fromisoformat(e["spent_date"])
        day_label = DAY_ABBR[entry_date.weekday()]
        notes = (e.get("notes") or "").strip()
        projects[project][task][day_label].append((notes, e["hours"]))
    return projects


def _format_plain(projects: dict, start: date, end: date) -> str:
    """Plain text summary for the email fallback."""
    start_fmt = start.strftime("%-d %b")
    end_fmt = end.strftime("%-d %b")
    lines = [f"WEEKLY SUMMARY (Fri {start_fmt} \u2013 Thu {end_fmt})", ""]

    total_hours = 0.0
    for project_name in sorted(projects):
        tasks = projects[project_name]
        project_hours = sum(h for t in tasks.values() for d in t.values() for _, h in d)
        total_hours += project_hours
        lines.append(f"{project_name} \u2014 {project_hours:.2f}h")

        for task_name in sorted(tasks):
            days = tasks[task_name]
            task_hours = sum(h for d in days.values() for _, h in d)
            lines.append("")
            lines.append(f"  {task_name} \u2014 {task_hours:.2f}h")

            for day in DAY_ORDER:
                if day not in days:
                    continue
                day_entries = days[day]
                day_hours = sum(h for _, h in day_entries)
                notes_list = [" ".join(n.split()) for n, _ in day_entries if n]
                if len(notes_list) <= 1:
                    note = notes_list[0] if notes_list else ""
                    if note:
                        lines.append(f"    {day}: {note} ({day_hours:.2f}h)")
                    else:
                        lines.append(f"    {day}: ({day_hours:.2f}h)")
                else:
                    lines.append(f"    {day} ({day_hours:.2f}h):")
                    for note in notes_list:
                        lines.append(f"      \u00b7 {note}")

        lines.append("")

    lines.append(f"TOTAL: {total_hours:.2f}h")
    return "\n".join(lines)


def _format_html(projects: dict, start: date, end: date) -> str:
    """HTML summary with a table layout."""
    start_fmt = start.strftime("%-d %b")
    end_fmt = end.strftime("%-d %b")

    rows: list[str] = []
    total_hours = 0.0

    for project_name in sorted(projects):
        tasks = projects[project_name]
        project_hours = sum(h for t in tasks.values() for d in t.values() for _, h in d)
        total_hours += project_hours

        rows.append(
            f'<tr style="background:#f0f0f0">'
            f'<td colspan="3" style="padding:8px;font-weight:bold">'
            f'{escape(project_name)}</td>'
            f'<td style="padding:8px;font-weight:bold;text-align:right">'
            f'{project_hours:.2f}h</td></tr>'
        )

        for task_name in sorted(tasks):
            days = tasks[task_name]
            task_hours = sum(h for d in days.values() for _, h in d)

            rows.append(
                f'<tr><td style="padding:6px 8px 6px 24px;font-weight:600" '
                f'colspan="3">{escape(task_name)}</td>'
                f'<td style="padding:6px 8px;text-align:right;font-weight:600">'
                f'{task_hours:.2f}h</td></tr>'
            )

            for day in DAY_ORDER:
                if day not in days:
                    continue
                day_entries = days[day]
                day_hours = sum(h for _, h in day_entries)
                notes_list = [" ".join(n.split()) for n, _ in day_entries if n]
                notes_html = "<br>".join(escape(n) for n in notes_list) if notes_list else ""

                rows.append(
                    f'<tr style="color:#555;border-top:1px solid #e0e0e0">'
                    f'<td style="padding:6px 8px 6px 40px;vertical-align:top">{day}</td>'
                    f'<td style="padding:6px 8px;vertical-align:top">{notes_html}</td>'
                    f'<td></td>'
                    f'<td style="padding:6px 8px;text-align:right;vertical-align:top">{day_hours:.2f}h</td></tr>'
                )

    return (
        f'<div style="font-family:sans-serif;max-width:700px">'
        f'<h2 style="margin-bottom:4px">Weekly Summary</h2>'
        f'<p style="color:#666;margin-top:0">Fri {start_fmt} \u2013 Thu {end_fmt}</p>'
        f'<table style="width:100%;border-collapse:collapse;border:1px solid #ddd">'
        f'<thead><tr style="background:#333;color:#fff">'
        f'<th style="padding:8px;text-align:left">Day</th>'
        f'<th style="padding:8px;text-align:left">Notes</th>'
        f'<th style="padding:8px"></th>'
        f'<th style="padding:8px;text-align:right">Hours</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody>'
        f'<tfoot><tr style="background:#333;color:#fff;font-weight:bold">'
        f'<td colspan="3" style="padding:8px">Total</td>'
        f'<td style="padding:8px;text-align:right">{total_hours:.2f}h</td>'
        f'</tr></tfoot></table></div>'
    )


def main():
    start, end = _get_date_range()
    print(f"Fetching entries from {start} to {end}...")
    entries = _fetch_entries(start, end)

    if not entries:
        print("No time entries found for this period.")
        return

    projects = _group_entries(entries)
    plain = _format_plain(projects, start, end)
    html = _format_html(projects, start, end)
    print(plain)

    subject = f"Weekly Summary (Fri {start.strftime('%-d %b')} \u2013 Thu {end.strftime('%-d %b')})"
    send_email(subject, plain, html=html)
    print("\nSent via email.")

    send_message(f"{subject} has been emailed.")
    print("Telegram reminder sent.")


if __name__ == "__main__":
    main()
