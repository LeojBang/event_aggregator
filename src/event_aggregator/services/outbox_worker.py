import asyncio
import logging

import httpx

from event_aggregator.clients.capashino import CapashinoClient
from event_aggregator.core.config import settings
from event_aggregator.core.db import SessionLocal
from event_aggregator.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)


async def _run_outbox_worker() -> None:
    client = CapashinoClient(settings.CAPASHINO_URL, settings.CAPASHINO_API_KEY)
    while True:
        await asyncio.sleep(settings.OUTBOX_POLL_INTERVAL_SECONDS)
        try:
            async with SessionLocal() as session:
                repo = OutboxRepository(session)
                pending = await repo.get_pending(limit=10)
                for msg in pending:
                    try:
                        logger.info(
                            "Processing outbox %s: %s", msg.outbox_id, msg.payload
                        )
                        payload = msg.payload
                        event_name = payload["event_name"]
                        message = (
                            f"Вы успешно зарегистрированы на мероприятие - {event_name}"
                        )
                        await client.send_notification(
                            message=message,
                            reference_id=payload["ticket_id"],
                            idempotency_key=str(msg.outbox_id),
                        )
                        await repo.mark_sent(msg.outbox_id)
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 409:
                            await repo.mark_sent(msg.outbox_id)
                        else:
                            logger.exception(
                                "Failed to process outbox %s", msg.outbox_id
                            )
                            await repo.mark_failed(msg.outbox_id, error=str(e))
                    except httpx.RequestError as e:
                        logger.exception(
                            "Network error while processing outbox %s", msg.outbox_id
                        )
                        await repo.mark_failed(msg.outbox_id, error=str(e))
                    except Exception as e:
                        logger.exception("Failed outbox %s", msg.outbox_id)
                        await repo.mark_failed(msg.outbox_id, error=str(e))
                await session.commit()
        except Exception:
            logger.exception("Outbox worker iteration failed")
