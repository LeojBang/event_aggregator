import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, UUID, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from event_aggregator.core.db import Base
from event_aggregator.models.enums import OutboxEventType, OutboxStatus


class Outbox(Base):
    __tablename__ = "outbox"

    outbox_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_type: Mapped[OutboxEventType] = mapped_column(
        Enum(
            OutboxEventType,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=20,
        )
    )
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[OutboxStatus] = mapped_column(
        Enum(
            OutboxStatus,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=20,
        ),
        index=True,
        default=OutboxStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(String, nullable=True)
