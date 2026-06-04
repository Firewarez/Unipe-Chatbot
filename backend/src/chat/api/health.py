"""Health checks for dependencies."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

from sqlalchemy import text

from chat.api.config import settings
from chat.infrastructure.data.database import engine
from chat.infrastructure.external_services.chroma_service import ChromaDBService
from chat.infrastructure.external_services.ollama_service import OllamaService


def health_live() -> Dict[str, str]:
    return {"status": "healthy"}


def health_ready() -> Dict[str, object]:
    checks = {
        "database": _check_database(),
        "chroma": _check_chroma(),
        "ollama": _check_ollama(),
        "rabbitmq": _check_rabbitmq(),
        "logs_directory": _check_logs_directory(),
    }
    overall = "healthy"
    if any(result["status"] == "unhealthy" for result in checks.values()):
        overall = "unhealthy"
    elif any(result["status"] in {"degraded", "skipped"} for result in checks.values()):
        overall = "degraded"
    return {"status": overall, "checks": checks}


def _check_database() -> Dict[str, object]:
    start = time.monotonic()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "latency_ms": _elapsed_ms(start)}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


def _check_chroma() -> Dict[str, object]:
    start = time.monotonic()
    try:
        service = ChromaDBService(collection_name=settings.CHROMA_COLLECTION)
        service.contar_documentos()
        return {"status": "healthy", "latency_ms": _elapsed_ms(start)}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


def _check_ollama() -> Dict[str, object]:
    start = time.monotonic()
    try:
        service = OllamaService(model_name=settings.AI_MODEL)
        service.health_check()
        return {"status": "healthy", "latency_ms": _elapsed_ms(start)}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


def _check_rabbitmq() -> Dict[str, object]:
    if not settings.MESSAGING_ENABLED:
        return {"status": "skipped", "details": "messaging disabled"}
    try:
        import pika  # type: ignore
    except Exception as exc:
        return {"status": "unhealthy", "error": f"pika missing: {exc}"}

    start = time.monotonic()
    try:
        params = pika.URLParameters(settings.RABBITMQ_URL)
        params.socket_timeout = settings.RABBITMQ_TIMEOUT_S
        params.blocked_connection_timeout = settings.RABBITMQ_TIMEOUT_S
        connection = pika.BlockingConnection(params)
        connection.close()
        return {"status": "healthy", "latency_ms": _elapsed_ms(start)}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


def _elapsed_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


def _check_logs_directory() -> Dict[str, object]:
    start = time.monotonic()
    log_dir = Path(settings.LOG_DIR)
    test_file = log_dir / ".healthcheck_write_test"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return {"status": "healthy", "latency_ms": _elapsed_ms(start)}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}
