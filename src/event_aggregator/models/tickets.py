from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from event_aggregator.core.db import Base


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    seat: Mapped[str] = mapped_column(String)
