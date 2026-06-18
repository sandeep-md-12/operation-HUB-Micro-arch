import enum
from sqlalchemy import Column, String, Enum, Boolean
from app.utils.database import Base


class NotificationState(str, enum.Enum):
    pending = "Pending"
    sent = "Sent"
    failed = "Failed"


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String, primary_key=True)
    recipient_id = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    state = Column(Enum(NotificationState), default=NotificationState.pending, nullable=False)
    retry_count = Column(String, default="0", nullable=False)

    def __eq__(self, other):
        return isinstance(other, Notification) and self.notification_id == other.notification_id

    def __hash__(self):
        return hash(self.notification_id)

    def __str__(self):
        return f"Notification({self.notification_id}, {self.recipient_id}, {self.state})"

    def __repr__(self):
        return self.__str__()
