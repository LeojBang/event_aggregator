from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.models.places import Place


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, place_data: dict) -> None:
        stmt = select(Place).where(Place.id == place_data["id"])

        result = await self._session.execute(stmt)

        place = result.scalar_one_or_none()

        if not place:
            db_place = Place(
                id=place_data["id"],
                name=place_data["name"],
                city=place_data["city"],
                address=place_data["address"],
                seats_pattern=place_data["seats_pattern"],
                changed_at=datetime.fromisoformat(place_data["changed_at"]),
            )
            self._session.add(db_place)
        else:
            place.name = place_data["name"]
            place.city = place_data["city"]
            place.address = place_data["address"]
            place.seats_pattern = place_data["seats_pattern"]
            place.changed_at = datetime.fromisoformat(place_data["changed_at"])
