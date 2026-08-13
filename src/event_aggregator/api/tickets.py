from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.clients.event_provider import EventsProviderClient
from event_aggregator.core.config import settings
from event_aggregator.core.db import get_db
from event_aggregator.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
    RegistrationClosedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)
from event_aggregator.repositories.events import EventRepository
from event_aggregator.repositories.tickets import TicketRepository
from event_aggregator.schemas.tickets import (
    CreateTicketRequestSchema,
    CreateTicketResponseSchema,
    DeleteTicketResponseSchema,
)
from event_aggregator.services.seats import SeatsService
from event_aggregator.services.tickets import CreateTicketService, DeleteTicketService

router = APIRouter()


def _get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        settings.EVENTS_PROVIDER_URL,
        settings.EVENTS_PROVIDER_API_KEY,
    )


@router.post(
    "/api/tickets",
    response_model=CreateTicketResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    payload: CreateTicketRequestSchema,
    session: AsyncSession = Depends(get_db),
) -> CreateTicketResponseSchema:
    client = _get_events_provider_client()
    event_repo = EventRepository(session)
    seats_service = SeatsService(event_repo, client)
    service = CreateTicketService(
        event_repo,
        TicketRepository(session),
        seats_service,
        client,
    )

    try:
        ticket_id = await service.create(
            event_id=payload.event_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            seat=payload.seat,
        )
        await session.commit()
    except EventNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Event not found") from exc
    except EventNotPublishedError as exc:
        raise HTTPException(status_code=400, detail="Event is not published") from exc
    except RegistrationClosedError as exc:
        raise HTTPException(status_code=400, detail="Registration is closed") from exc
    except SeatNotAvailableError as exc:
        raise HTTPException(status_code=400, detail="Seat is not available") from exc

    return CreateTicketResponseSchema(ticket_id=ticket_id)


@router.delete("/api/tickets/{ticket_id}", response_model=DeleteTicketResponseSchema)
async def delete_ticket(
    ticket_id: str,
    session: AsyncSession = Depends(get_db),
) -> DeleteTicketResponseSchema:
    client = _get_events_provider_client()
    service = DeleteTicketService(TicketRepository(session), client)

    try:
        await service.delete(ticket_id)
        await session.commit()
    except TicketNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Ticket not found") from exc

    return DeleteTicketResponseSchema(success=True)
