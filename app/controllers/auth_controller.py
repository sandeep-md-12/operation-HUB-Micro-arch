import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.schemas.user import UserRegister, UserLogin
from app.utils.response import success_response, error_response
from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError, InactiveUserError
from fastapi.responses import JSONResponse


class AuthController:
    def __init__(self, db: AsyncSession):
        self.service = AuthService(db)

    async def register(self, payload: UserRegister) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.register(payload.username, payload.email, payload.password, payload.role, request_id)
            return success_response(201, result, request_id)
        except UserAlreadyExistsError as e:
            return error_response(409, str(e), request_id)

    async def login(self, payload: UserLogin) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.login(payload.username, payload.password, request_id)
            return success_response(200, result, request_id)
        except (InvalidCredentialsError, InactiveUserError) as e:
            return error_response(401, str(e), request_id)
