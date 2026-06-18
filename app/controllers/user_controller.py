import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from app.schemas.user import UserUpdate
from app.utils.response import success_response, error_response
from app.utils.exceptions import UserNotFoundError
from fastapi.responses import JSONResponse


class UserController:
    def __init__(self, db: AsyncSession):
        self.service = UserService(db)

    async def get_user(self, user_id: str) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.get_user(user_id, request_id)
            return success_response(200, result, request_id)
        except UserNotFoundError as e:
            return error_response(404, str(e), request_id)

    async def list_users(self) -> JSONResponse:
        request_id = str(uuid.uuid4())
        result = await self.service.list_users(request_id)
        return success_response(200, result, request_id)

    async def update_user(self, user_id: str, payload: UserUpdate) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            print(f"Updating user {user_id} with payload {payload.dict()} (request_id={request_id})")
            result = await self.service.update_user(user_id, payload.is_active, payload.role, request_id)
            return success_response(200, result, request_id)
        except UserNotFoundError as e:
            return error_response(404, str(e), request_id)
