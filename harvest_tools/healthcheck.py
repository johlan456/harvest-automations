"""Healthchecks.io ping helpers. No-op if URL is None or empty."""

import urllib.error
import urllib.request


def _ping(url: str | None, suffix: str = "") -> None:
    if not url:
        return
    try:
        urllib.request.urlopen(url.rstrip("/") + suffix, timeout=10)
    except (urllib.error.URLError, TimeoutError, OSError):
        pass


def start(url: str | None) -> None:
    _ping(url, "/start")


def success(url: str | None) -> None:
    _ping(url)


def fail(url: str | None) -> None:
    _ping(url, "/fail")
