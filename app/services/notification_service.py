import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationState
from app.repositories.notification_repository import NotificationRepository
from app.utils.cache import redis_client
from app.utils.exceptions import NotificationNotFoundError
from app.utils.websocket import manager

UNREAD_TTL = 300
CHANNEL = "notifications:job_events"


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificationRepository(db)

    async def create(self, recipient_id: str, subject: str, body: str, request_id: str) -> dict:
        n = Notification(
            notification_id=str(uuid.uuid4()),
            recipient_id=recipient_id,
            subject=subject,
            body=body,
        )
        n = await self.repo.create(n)
        await redis_client.delete(f"notification:unread:{recipient_id}")
        data = self._to_dict(n)
        await manager.push(recipient_id, data)
        await redis_client.publish(CHANNEL, json.dumps({
            "actor_id": recipient_id,
            "subject": subject,
            "body": body,
            "skip_persist": True
        }))
        return data

    async def get(self, notification_id: str, request_id: str) -> dict:
        n = await self.repo.get_by_id(notification_id)
        if not n:
            raise NotificationNotFoundError("Notification not found")
        return self._to_dict(n)

    async def list_for_user(self, recipient_id: str, request_id: str) -> list[dict]:
        notifications = await self.repo.get_by_recipient(recipient_id)
        return [self._to_dict(n) for n in notifications]

    async def get_unread(self, recipient_id: str, request_id: str) -> list[dict]:
        cache_key = f"notification:unread:{recipient_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        notifications = await self.repo.get_unread_by_recipient(recipient_id)
        data = [self._to_dict(n) for n in notifications]
        await redis_client.setex(cache_key, UNREAD_TTL, json.dumps(data))
        return data

    async def mark_read(self, notification_id: str, request_id: str) -> dict:
        n = await self.repo.get_by_id(notification_id)
        if not n:
            raise NotificationNotFoundError("Notification not found")
        n.is_read = True
        n = await self.repo.update(n)
        await redis_client.delete(f"notification:unread:{n.recipient_id}")
        return self._to_dict(n)

    def _to_dict(self, n: Notification) -> dict:
        return {
            "notification_id": n.notification_id,
            "recipient_id": n.recipient_id,
            "subject": n.subject,
            "body": n.body,
            "is_read": n.is_read,
            "state": n.state,
            "retry_count": n.retry_count,
        }
