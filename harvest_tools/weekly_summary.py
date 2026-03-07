"""Weekly summary of Harvest time entries, delivered via Telegram."""

from collections import defaultdict
from datetime import date, timedelta

from .client import get_client
from .telegram import send_message

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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


def _format_summary(entries: list[dict], start: date, end: date) -> str:
    """Group entries by project → task → day and format as a text summary."""
    # Structure: {project: {task: {day_str: [(notes, hours)]}}}
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

    start_fmt = start.strftime("%-d %b")
    end_fmt = end.strftime("%-d %b")
    lines = [f"WEEKLY SUMMARY (Fri {start_fmt} \u2013 Thu {end_fmt})", ""]

    total_hours = 0.0
    # Sort projects alphabetically
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

            # Order days Fri, Sat, Sun, Mon, Tue, Wed, Thu
            day_order = ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]
            for day in day_order:
                if day not in days:
                    continue
                day_entries = days[day]
                day_hours = sum(h for _, h in day_entries)
                # Collapse newlines within notes
                notes_list = [
                    " ".join(n.split()) for n, _ in day_entries if n
                ]
                if len(notes_list) <= 1:
                    note = notes_list[0] if notes_list else ""
                    if note:
                        lines.append(f"    {day}: {note} ({day_hours:.2f}h)")
                    else:
                        lines.append(f"    {day}: ({day_hours:.2f}h)")
                else:
                    lines.append(f"    {day} ({day_hours:.2f}h):")
                    for note in notes_list:
                        lines.append(f"      · {note}")

        lines.append("")

    lines.append(f"TOTAL: {total_hours:.2f}h")
    return "\n".join(lines)


def main():
    start, end = _get_date_range()
    print(f"Fetching entries from {start} to {end}...")
    entries = _fetch_entries(start, end)

    if not entries:
        print("No time entries found for this period.")
        return

    summary = _format_summary(entries, start, end)
    print(summary)
    send_message(summary)
    print("\nSent to Telegram.")


if __name__ == "__main__":
    main()
