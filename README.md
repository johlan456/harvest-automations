# Harvest Automations

Personal automation tools for the [Harvest](https://www.getharvest.com/) time tracking API.

## Tools

- **runaway-timer** — Sends a Telegram notification when a running timer exceeds a configurable threshold (default: 1h). Run on a schedule to catch forgotten timers.
- **weekly-summary** — Sends a weekly summary of time entries (Fri–Thu) via Telegram, grouped by project and task. Run on Thursdays at 16:00 to prepare for Friday standup.
- **timesheet-reminder** — *(coming soon)* Monday morning reminder to submit your timesheet.
- **monthly-export** — *(coming soon)* Export time entries for a specific client/project/task.

## Setup

1. Get a [Harvest Personal Access Token](https://id.getharvest.com/developers)
2. Set up a [Telegram bot](https://t.me/BotFather) for notifications
3. Copy `.env.example` to `.env` and fill in your credentials
4. Install dependencies:
```
uv sync
```

## Usage

```
uv run runaway-timer
uv run weekly-summary
```

### Cron examples

```cron
# Check for runaway timers every 15 minutes during work hours
*/15 9-17 * * 1-5 cd /home/johlan/dev/agileworks/harvest && uv run runaway-timer

# Weekly summary every Thursday at 16:00
0 16 * * 4 cd /home/johlan/dev/agileworks/harvest && uv run weekly-summary
```

## Configuration

See `.env.example` for all available settings.
