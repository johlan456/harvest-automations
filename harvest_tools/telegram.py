"""Shared Telegram notification helper."""

import os
from pathlib import Path

import httpx

from .retry import with_retries

TIMEOUT = httpx.Timeout(30.0)


def send_message(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = with_retries(
        lambda: httpx.post(
            url, json={"chat_id": chat_id, "text": text}, timeout=TIMEOUT
        ),
        exceptions=(httpx.TransportError,),
    )
    resp.raise_for_status()


def send_document(file_path: str | Path, caption: str = "") -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    resp = with_retries(
        lambda: _post_document(url, chat_id, file_path, caption),
        exceptions=(httpx.TransportError,),
    )
    resp.raise_for_status()


def _post_document(
    url: str, chat_id: str, file_path: str | Path, caption: str
) -> httpx.Response:
    with open(file_path, "rb") as f:
        return httpx.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (Path(file_path).name, f)},
            timeout=TIMEOUT,
        )
