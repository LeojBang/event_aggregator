import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.models import Outbox
from event_aggregator.models.enums import OutboxEventType, OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, outbox_id: uuid.UUID) -> Outbox | None:
        stmt = select(Outbox).where(Outbox.outbox_id == outbox_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, event_type: OutboxEventType, payload: dict) -> Outbox:
        outbox = Outbox(event_type=event_type, payload=payload)
        self._session.add(outbox)
        return outbox

    async def get_pending(self, *, limit: int = 10) -> list[Outbox]:
        stmt = (
            select(Outbox)
            .where(Outbox.status == OutboxStatus.PENDING)
            .order_by(Outbox.created_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def mark_sent(self, outbox_id: uuid.UUID) -> None:
        outbox = await self.get_by_id(outbox_id)
        if outbox:
            outbox.status = OutboxStatus.SENT
            outbox.last_error = None

    async def mark_failed(self, outbox_id: uuid.UUID, error: str) -> None:
        outbox = await self.get_by_id(outbox_id)
        if outbox:
            outbox.attempts += 1
            outbox.last_error = error
