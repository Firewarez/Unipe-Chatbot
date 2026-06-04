"""Observability utilities: structured logs, correlation id, and metrics."""
from __future__ import annotations

import contextvars
import json
import logging
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Iterable, Tuple

from fastapi import Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return correlation_id_var.get()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }
        for key in ("method", "path", "status_code", "duration_ms", "client_ip", "user_agent"):
            if hasattr(record, key):
                log[key] = getattr(record, key)
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)


def configure_logging(level: str) -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


class MetricsCollector:
    def __init__(self, buckets: Iterable[float] | None = None) -> None:
        self.enabled = True
        self._buckets = sorted(buckets or (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0))
        self._lock = threading.Lock()
        self._request_counts: Dict[Tuple[str, str, int], int] = {}
        self._duration_stats: Dict[Tuple[str, str], Dict[str, object]] = {}
        self._business_counters: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], int] = {}

    def observe_request(self, method: str, path: str, status_code: int, duration_s: float) -> None:
        if not self.enabled:
            return
        key_count = (method, path, status_code)
        key_duration = (method, path)
        with self._lock:
            self._request_counts[key_count] = self._request_counts.get(key_count, 0) + 1
            if key_duration not in self._duration_stats:
                self._duration_stats[key_duration] = {
                    "buckets": [0 for _ in self._buckets],
                    "sum": 0.0,
                    "count": 0,
                }
            stat = self._duration_stats[key_duration]
            stat["sum"] = float(stat["sum"]) + duration_s
            stat["count"] = int(stat["count"]) + 1
            for idx, bound in enumerate(self._buckets):
                if duration_s <= bound:
                    stat["buckets"][idx] = int(stat["buckets"][idx]) + 1

    def render(self) -> str:
        lines = [
            "# HELP http_requests_total Total HTTP requests",
            "# TYPE http_requests_total counter",
        ]
        for (method, path, status), count in sorted(self._request_counts.items()):
            lines.append(
                f'http_requests_total{{method="{_escape_label(method)}",path="{_escape_label(path)}",status="{status}"}} {count}'
            )

        lines.extend([
            "# HELP http_request_duration_seconds HTTP request duration",
            "# TYPE http_request_duration_seconds histogram",
        ])
        for (method, path), stat in sorted(self._duration_stats.items()):
            cumulative = 0
            for bound, bucket_count in zip(self._buckets, stat["buckets"]):
                cumulative += int(bucket_count)
                lines.append(
                    "http_request_duration_seconds_bucket"
                    f'{{method="{_escape_label(method)}",path="{_escape_label(path)}",le="{bound}"}} {cumulative}'
                )
            lines.append(
                "http_request_duration_seconds_bucket"
                f'{{method="{_escape_label(method)}",path="{_escape_label(path)}",le="+Inf"}} {int(stat["count"])}'
            )
            lines.append(
                "http_request_duration_seconds_sum"
                f'{{method="{_escape_label(method)}",path="{_escape_label(path)}"}} {float(stat["sum"])}'
            )
            lines.append(
                "http_request_duration_seconds_count"
                f'{{method="{_escape_label(method)}",path="{_escape_label(path)}"}} {int(stat["count"])}'
            )

        lines.extend([
            "# HELP app_events_total Application business events",
            "# TYPE app_events_total counter",
        ])
        for (event_name, labels_tuple), count in sorted(self._business_counters.items()):
            labels = [f'event="{_escape_label(event_name)}"']
            labels.extend([f'{_escape_label(k)}="{_escape_label(v)}"' for k, v in labels_tuple])
            lines.append(f'app_events_total{{{",".join(labels)}}} {count}')

        return "\n".join(lines) + "\n"

    def inc_event(self, event_name: str, **labels: str) -> None:
        if not self.enabled:
            return
        key = (event_name, tuple(sorted((k, str(v)) for k, v in labels.items())))
        with self._lock:
            self._business_counters[key] = self._business_counters.get(key, 0) + 1


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', "\\\"")


metrics_collector = MetricsCollector()


def metrics_endpoint() -> PlainTextResponse:
    if not metrics_collector.enabled:
        return PlainTextResponse("metrics disabled", status_code=503)
    return PlainTextResponse(metrics_collector.render(), media_type="text/plain; version=0.0.4")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics: MetricsCollector | None = None) -> None:
        super().__init__(app)
        self._metrics = metrics
        self._logger = logging.getLogger("chat.api.request")

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        token = correlation_id_var.set(correlation_id)
        start = time.monotonic()
        status_code = 500
        response = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_s = time.monotonic() - start
            duration_ms = int(duration_s * 1000)
            if self._metrics:
                self._metrics.observe_request(request.method, request.url.path, status_code, duration_s)
            self._logger.info(
                "http_request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("User-Agent"),
                },
            )
            if response is not None:
                response.headers["X-Correlation-ID"] = correlation_id
            correlation_id_var.reset(token)
