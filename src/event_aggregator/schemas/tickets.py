from pydantic import BaseModel, EmailStr, Field


class CreateTicketRequestSchema(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: EmailStr
    seat: str = Field(min_length=1)
    idempotency_key: str | None = None


class CreateTicketResponseSchema(BaseModel):
    ticket_id: str


class DeleteTicketResponseSchema(BaseModel):
    success: bool
