from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlaceShortSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    city: str
    address: str


class PlaceDetailSchema(PlaceShortSchema):
    seats_pattern: str


class EventListItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    place: PlaceShortSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    place: PlaceDetailSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventListResponseSchema(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventListItemSchema]


class SeatsResponseSchema(BaseModel):
    event_id: str
    available_seats: list[str]
