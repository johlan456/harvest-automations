This is a public GitHub repository. Never commit secrets, tokens, API keys, or credentials.

All secrets must live in `.env` (which is gitignored). Use `.env.example` for documenting required variables with placeholder values only.

## Project

Python tools for automating personal Harvest time tracking tasks. Uses `uv` for dependency management.

## Structure

- `harvest_tools/client.py` — shared Harvest API client
- `harvest_tools/telegram.py` — shared Telegram notification helper
- `harvest_tools/runaway_timer.py` — alerts when a timer has been running too long
- `harvest_tools/monthly_export.py` — exports T4A (Tracks 4 Africa) entries from HEV004 project to XLSX
- `harvest_tools/weekly_summary.py` — weekly Fri–Thu time summary sent via Telegram
