from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from event_aggregator.core.db import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    idempotency_key: Mapped[str] = mapped_column(primary_key=True, unique=True)
    ticket_id: Mapped[str] = mapped_column(String)
    event_id: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    seat: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
