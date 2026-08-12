from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from event_aggregator.core.db import Base
from event_aggregator.models.enums import EventStatus

if TYPE_CHECKING:
    from event_aggregator.models.places import Place


class Event(Base):
    __tablename__ = "events"

    __table_args__ = (Index("ix_events_event_time", "event_time"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, native_enum=False, length=20)
    )
    number_of_visitors: Mapped[int] = mapped_column(Integer, default=0)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False)

    place: Mapped["Place"] = relationship(back_populates="events")
