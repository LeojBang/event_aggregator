class EventNotFoundError(Exception):
    pass


class EventNotPublishedError(Exception):
    pass


class RegistrationClosedError(Exception):
    pass


class SeatNotAvailableError(Exception):
    pass


class TicketNotFoundError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass
