"""Outbox repository for integration events."""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from chat.domain.events.integration_event import IntegrationEvent
from chat.infrastructure.data.database import OutboxEventModel


class OutboxRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(self, event: IntegrationEvent) -> None:
        model = OutboxEventModel(
            id=event.event_id,
            event_type=event.event_type,
            payload=json.dumps(event.to_dict(), ensure_ascii=False),
            occurred_at=datetime.utcnow(),
            published_at=None,
        )
        self._db.add(model)
        self._db.commit()

    def mark_published(self, event_id: str) -> None:
        model = self._db.query(OutboxEventModel).filter(OutboxEventModel.id == event_id).first()
        if model:
            model.published_at = datetime.utcnow()
            self._db.commit()

    def list_pending(self, limit: int = 100) -> list[OutboxEventModel]:
        return (
            self._db.query(OutboxEventModel)
            .filter(OutboxEventModel.published_at.is_(None))
            .order_by(OutboxEventModel.occurred_at.asc())
            .limit(limit)
            .all()
        )
