from enum import StrEnum


class EventStatus(StrEnum):
    NEW = "new"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    REGISTRATION_CLOSED = "registration_closed"
    FINISHED = "finished"


class OutboxEventType(StrEnum):
    TICKET_PURCHASED = "ticket_purchased"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"


class TicketStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
