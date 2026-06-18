from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: str) -> Notification | None:
        result = await self.db.execute(select(Notification).where(Notification.notification_id == notification_id))
        return result.scalar_one_or_none()

    async def get_by_recipient(self, recipient_id: str) -> list[Notification]:
        result = await self.db.execute(select(Notification).where(Notification.recipient_id == recipient_id))
        return list(result.scalars().all())

    async def get_unread_by_recipient(self, recipient_id: str) -> list[Notification]:
        result = await self.db.execute(
            select(Notification).where(
                Notification.recipient_id == recipient_id,
                Notification.is_read == False
            )
        )
        return list(result.scalars().all())

    async def update(self, notification: Notification) -> Notification:
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
