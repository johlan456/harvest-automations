"""Check for running timers and send a Telegram notification if any exceed the threshold."""

import os
import sys

from .client import get_client
from .telegram import send_message

DEFAULT_THRESHOLD_HOURS = 1


def main():
    threshold = float(os.environ.get("RUNAWAY_THRESHOLD_HOURS", DEFAULT_THRESHOLD_HOURS))

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

        if hours >= threshold:
            alerts.append(f"{project} / {task} — {hours:.1f}h")

    if alerts:
        msg = "Timer still running:\n" + "\n".join(alerts)
        print(msg)
        send_message(msg)
        sys.exit(1)
    else:
        for entry in entries:
            print(f"  Running: {entry['project']['name']} / {entry['task']['name']} — {entry['hours']:.1f}h (under {threshold}h)")


if __name__ == "__main__":
    main()
