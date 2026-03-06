"""Shared Telegram notification helper."""

import os

import httpx


def send_message(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = httpx.post(url, json={"chat_id": chat_id, "text": text})
    resp.raise_for_status()
