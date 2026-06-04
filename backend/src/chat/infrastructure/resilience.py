"""Resilience utilities: retry, circuit breaker, and timeout."""
from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Callable, Optional, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=8)


class CircuitBreakerOpen(RuntimeError):
    """Raised when the circuit breaker is open."""


class CircuitBreaker:
    def __init__(self, fail_max: int, reset_timeout_s: float) -> None:
        self._fail_max = max(1, fail_max)
        self._reset_timeout_s = max(0.1, reset_timeout_s)
        self._failure_count = 0
        self._state = "closed"
        self._opened_at: Optional[float] = None
        self._lock = threading.Lock()

    def call(self, func: Callable[[], T]) -> T:
        with self._lock:
            if self._state == "open":
                if self._opened_at and (time.monotonic() - self._opened_at) >= self._reset_timeout_s:
                    self._state = "half-open"
                else:
                    raise CircuitBreakerOpen("circuit breaker is open")

        try:
            result = func()
        except Exception:
            self._record_failure()
            raise
        else:
            self._record_success()
            return result

    def _record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            if self._failure_count >= self._fail_max:
                self._state = "open"
                self._opened_at = time.monotonic()

    def _record_success(self) -> None:
        with self._lock:
            self._failure_count = 0
            self._state = "closed"
            self._opened_at = None


def run_with_timeout(func: Callable[..., T], timeout_s: Optional[float], *args, **kwargs) -> T:
    if not timeout_s or timeout_s <= 0:
        return func(*args, **kwargs)

    future = _executor.submit(func, *args, **kwargs)
    try:
        return future.result(timeout=timeout_s)
    except FutureTimeoutError as exc:
        future.cancel()
        raise TimeoutError(f"timeout after {timeout_s:.2f}s") from exc


class ResiliencePolicy:
    def __init__(
        self,
        name: str,
        timeout_s: Optional[float],
        retry_attempts: int,
        backoff_base_s: float,
        backoff_max_s: float,
        circuit_fail_max: int,
        circuit_reset_timeout_s: float,
    ) -> None:
        self._name = name
        self._timeout_s = timeout_s
        self._retry_attempts = max(1, retry_attempts)
        self._backoff_base_s = max(0.0, backoff_base_s)
        self._backoff_max_s = max(self._backoff_base_s, backoff_max_s)
        self._breaker = CircuitBreaker(circuit_fail_max, circuit_reset_timeout_s)

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        attempt = 1
        while True:
            try:
                return self._breaker.call(lambda: run_with_timeout(func, self._timeout_s, *args, **kwargs))
            except CircuitBreakerOpen:
                logger.warning("%s circuit breaker open", self._name)
                raise
            except Exception as exc:
                if attempt >= self._retry_attempts:
                    raise
                delay = min(self._backoff_base_s * (2 ** (attempt - 1)), self._backoff_max_s)
                logger.warning("%s attempt %s failed: %s. Retrying in %.2fs", self._name, attempt, exc, delay)
                time.sleep(delay)
                attempt += 1
