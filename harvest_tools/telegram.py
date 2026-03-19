"""Shared Telegram notification helper."""

import os
from pathlib import Path

import httpx


def send_message(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = httpx.post(url, json={"chat_id": chat_id, "text": text})
    resp.raise_for_status()


def send_document(file_path: str | Path, caption: str = "") -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, "rb") as f:
        resp = httpx.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (Path(file_path).name, f)},
        )
    resp.raise_for_status()
