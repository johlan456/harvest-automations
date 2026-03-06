"""Check for running timers and send a Telegram notification if any exceed the threshold."""

import json
import os
import sys
import time

from .client import get_client
from .telegram import send_message

DEFAULT_THRESHOLD_HOURS = 1
REALERT_INTERVAL_SECONDS = 3600
STATE_FILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "harvest-runaway-alerted.json")


def _load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    threshold = float(os.environ.get("RUNAWAY_THRESHOLD_HOURS", DEFAULT_THRESHOLD_HOURS))

    client = get_client()
    resp = client.get("/time_entries", params={"is_running": "true"})
    resp.raise_for_status()
    entries = resp.json()["time_entries"]

    if not entries:
        print("No running timers.")
        _save_state({})
        return

    state = _load_state()
    now = time.time()
    running_ids = set()

    alerts = []
    for entry in entries:
        hours = entry["hours"]
        project = entry["project"]["name"]
        task = entry["task"]["name"]
        entry_id = str(entry["id"])
        running_ids.add(entry_id)

        if hours < threshold:
            print(f"  Running: {project} / {task} — {hours:.1f}h (under {threshold}h)")
            continue

        last_alerted = state.get(entry_id, 0)
        if now - last_alerted < REALERT_INTERVAL_SECONDS:
            print(f"  Suppressed (already notified): {project} / {task} — {hours:.1f}h")
            continue

        alerts.append(f"{project} / {task} — {hours:.1f}h")
        state[entry_id] = now

    # Remove entries that are no longer running
    state = {eid: ts for eid, ts in state.items() if eid in running_ids}
    _save_state(state)

    if alerts:
        msg = "Timer still running:\n" + "\n".join(alerts)
        print(msg)
        send_message(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
