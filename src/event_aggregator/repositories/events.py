from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.models.enums import EventStatus
from event_aggregator.models.events import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

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
