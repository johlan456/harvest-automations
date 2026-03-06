"""Check for running timers that have been active too long."""

import sys
from datetime import datetime, timedelta

from .client import get_client

MAX_HOURS = 4


def main():
    client = get_client()
    resp = client.get("/time_entries", params={"is_running": "true"})
    resp.raise_for_status()
    entries = resp.json()["time_entries"]

    if not entries:
        print("No running timers.")
        return

    alerts = []
    for entry in entries:
        hours = entry["hours"]
        project = entry["project"]["name"]
        task = entry["task"]["name"]
        started = entry["timer_started_at"]

        if hours >= MAX_HOURS:
            alerts.append(
                f"  ALERT: {project} / {task} — {hours:.1f}h (started {started})"
            )
        else:
            print(f"  Running: {project} / {task} — {hours:.1f}h")

    if alerts:
        print(f"Timers running over {MAX_HOURS}h:")
        for alert in alerts:
            print(alert)
        sys.exit(1)


if __name__ == "__main__":
    main()
