from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.models.enums import TicketStatus
from event_aggregator.models.tickets import Ticket


class TicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, ticket_id: str) -> Ticket | None:
        stmt = select(Ticket).where(
            (Ticket.ticket_id == ticket_id) & (Ticket.status == TicketStatus.ACTIVE)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        ticket_id: str,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> Ticket:
        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        self._session.add(ticket)
        return ticket

    async def delete(self, ticket: Ticket) -> None:
        await self._session.execute(
            update(Ticket)
            .where(Ticket.ticket_id == ticket.ticket_id)
            .values(status=TicketStatus.CANCELLED)
        )

    async def count(self):
        stmt = select(func.count()).select_from(Ticket)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_cancelled(self):
        stmt = (
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.status == TicketStatus.CANCELLED)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
