from datetime import UTC, date, datetime, time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from event_aggregator.models.enums import EventStatus
from event_aggregator.models.events import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    def _apply_date_from(self, stmt, date_from: date | None):
        if date_from is None:
            return stmt
        start = datetime.combine(date_from, time.min, tzinfo=UTC)
        return stmt.where(Event.event_time >= start)

    async def count(self, date_from: date | None = None) -> int:
        stmt = select(func.count()).select_from(Event)
        stmt = self._apply_date_from(stmt, date_from)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def list(
        self,
        *,
        date_from: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Event]:
        stmt = (
            select(Event)
            .options(selectinload(Event.place))
            .order_by(Event.event_time)
            .offset(offset)
            .limit(limit)
        )
        stmt = self._apply_date_from(stmt, date_from)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, event_id: str) -> Event | None:
        stmt = (
            select(Event).options(selectinload(Event.place)).where(Event.id == event_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, event_data: dict) -> None:
        stmt = select(Event).where(Event.id == event_data["id"])

        result = await self._session.execute(stmt)

        event = result.scalar_one_or_none()

        if not event:
            db_event = Event(
                id=event_data["id"],
                name=event_data["name"],
                event_time=datetime.fromisoformat(event_data["event_time"]),
                registration_deadline=datetime.fromisoformat(
                    event_data["registration_deadline"]
                ),
                status=EventStatus(event_data["status"]),
                number_of_visitors=event_data["number_of_visitors"],
                changed_at=datetime.fromisoformat(event_data["changed_at"]),
                place_id=event_data["place"]["id"],
            )
            self._session.add(db_event)
        else:
            event.name = event_data["name"]
            event.event_time = datetime.fromisoformat(event_data["event_time"])
            event.registration_deadline = datetime.fromisoformat(
                event_data["registration_deadline"]
            )
            event.status = EventStatus(event_data["status"])
            event.number_of_visitors = event_data["number_of_visitors"]
            event.changed_at = datetime.fromisoformat(event_data["changed_at"])
            event.place_id = event_data["place"]["id"]
