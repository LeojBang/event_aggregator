from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.models.idempotency import IdempotencyRecord


class IdempotencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key(self, key: str) -> IdempotencyRecord | None:
        stmt = select(IdempotencyRecord).where(IdempotencyRecord.idempotency_key == key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(
        self,
        key: str,
        ticket_id: str,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> None:
        record = IdempotencyRecord(
            idempotency_key=key,
            ticket_id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )

        self._session.add(record)
