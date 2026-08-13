from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_aggregator.models.sync_metadata import SyncMetadata


class SyncMetadataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> SyncMetadata | None:
        stmt = select(SyncMetadata).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(
        self,
        last_sync_time: datetime,
        last_changed_at: datetime | None,
        sync_status: str,
    ) -> None:
        metadata = await self.get()

        if metadata is None:
            metadata = SyncMetadata(
                last_sync_time=last_sync_time,
                last_changed_at=last_changed_at,
                sync_status=sync_status,
            )
            self._session.add(metadata)
        else:
            metadata.last_sync_time = last_sync_time
            metadata.last_changed_at = last_changed_at
            metadata.sync_status = sync_status
