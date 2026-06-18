import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.notification_service import NotificationService
from app.services.feature_flag_service import FeatureFlagService
from app.schemas.notification import NotificationCreate
from app.utils.response import success_response, error_response
from app.utils.exceptions import NotificationNotFoundError, FeatureDisabledError
from fastapi.responses import JSONResponse


class NotificationController:
    def __init__(self, db: AsyncSession):
        self.service = NotificationService(db)
        self.flags = FeatureFlagService(db)

    async def create(self, payload: NotificationCreate) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            await self.flags.require_enabled("notifications", request_id)
        except FeatureDisabledError as e:
            return error_response(403, str(e), request_id)
        result = await self.service.create(payload.recipient_id, payload.subject, payload.body, request_id)
        return success_response(201, result, request_id)

    async def get(self, notification_id: str, current_user: dict) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.get(notification_id, request_id)
            if result["recipient_id"] != current_user["user_id"] and current_user["role"] != "Admin":
                return error_response(403, "Access denied", request_id)
            return success_response(200, result, request_id)
        except NotificationNotFoundError as e:
            return error_response(404, str(e), request_id)

    async def list_for_user(self, recipient_id: str, unread: bool = False) -> JSONResponse:
        request_id = str(uuid.uuid4())
        if unread:
            result = await self.service.get_unread(recipient_id, request_id)
        else:
            result = await self.service.list_for_user(recipient_id, request_id)
        return success_response(200, result, request_id)

    async def mark_read(self, notification_id: str, current_user: dict) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.get(notification_id, request_id)
            if result["recipient_id"] != current_user["user_id"] and current_user["role"] != "Admin":
                return error_response(403, "Access denied", request_id)
            result = await self.service.mark_read(notification_id, request_id)
            return success_response(200, result, request_id)
        except NotificationNotFoundError as e:
            return error_response(404, str(e), request_id)
