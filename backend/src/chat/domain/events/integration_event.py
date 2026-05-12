"""Integration event base type."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class IntegrationEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: str = field(default_factory=_utc_now_iso)
    event_type: str = "integration_event"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
