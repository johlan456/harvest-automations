# Harvest Automations

Personal automation tools for the [Harvest](https://www.getharvest.com/) time tracking API.

## Tools

- **runaway-timer** — Sends a Telegram notification when a running timer exceeds a configurable threshold (default: 1h). Run on a schedule to catch forgotten timers.
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
```

To run on a schedule, set up a cron job or systemd timer.

## Configuration

See `.env.example` for all available settings.
