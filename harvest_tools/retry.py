"""Retry helper for transient network failures (DNS hiccups, timeouts)."""

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def with_retries(
    func: Callable[[], T],
    *,
    exceptions: tuple[type[BaseException], ...],
    attempts: int = 4,
    base_delay: float = 2.0,
) -> T:
    """Call ``func``, retrying on ``exceptions`` with exponential backoff.

    Delays between attempts are base_delay * 2**n (2s, 4s, 8s by default).
    Re-raises the last exception once attempts are exhausted.
    """
    for attempt in range(attempts):
        try:
            return func()
        except exceptions:
            if attempt == attempts - 1:
                raise
            time.sleep(base_delay * (2**attempt))
    raise AssertionError("unreachable")
