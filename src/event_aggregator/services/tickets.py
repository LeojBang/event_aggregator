from datetime import UTC, datetime

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
    RegistrationClosedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)
from event_aggregator.models.enums import EventStatus
from event_aggregator.repositories.events import EventRepository
from event_aggregator.repositories.tickets import TicketRepository
from event_aggregator.services.seats import SeatsService


class CreateTicketService:
    def __init__(
        self,
        event_repo: EventRepository,
        ticket_repo: TicketRepository,
        seats_service: SeatsService,
        client: EventsProviderClient,
    ) -> None:
        self._event_repo = event_repo
        self._ticket_repo = ticket_repo
        self._seats_service = seats_service
        self._client = client

    async def create(
        self,
        *,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> str:
        event = await self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError
        if event.status != EventStatus.PUBLISHED.value:
            raise EventNotPublishedError
        if datetime.now(UTC) >= event.registration_deadline:
            raise RegistrationClosedError

        available_seats = await self._seats_service.get_available_seats(event_id)
        if seat not in available_seats:
            raise SeatNotAvailableError

        response = await self._client.register(
            event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        ticket_id = response["ticket_id"]

        await self._ticket_repo.create(
            ticket_id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        return ticket_id


class DeleteTicketService:
    def __init__(
        self,
        ticket_repo: TicketRepository,
        client: EventsProviderClient,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._client = client

    async def delete(self, ticket_id: str) -> None:
        ticket = await self._ticket_repo.get_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError

        await self._client.unregister(ticket.event_id, ticket_id=ticket_id)
        await self._ticket_repo.delete(ticket)
