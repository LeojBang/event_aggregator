from enum import StrEnum


class EventStatus(StrEnum):
    NEW = "new"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    REGISTRATION_CLOSED = "registration_closed"
