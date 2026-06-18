from pydantic import BaseModel
from typing import Optional
from app.models.notification import NotificationState


class NotificationCreate(BaseModel):
    recipient_id: str
    subject: str
    body: str


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    state: Optional[NotificationState] = None


class NotificationResponse(BaseModel):
    notification_id: str
    recipient_id: str
    subject: str
    body: str
    is_read: bool
    state: str
    retry_count: str

    model_config = {"from_attributes": True}
