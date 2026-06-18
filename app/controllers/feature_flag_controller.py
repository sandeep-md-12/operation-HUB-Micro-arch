import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.feature_flag_service import FeatureFlagService
from app.schemas.feature_flag import FeatureFlagCreate, FeatureFlagUpdate
from app.utils.response import success_response, error_response
from app.utils.exceptions import FeatureFlagNotFoundError
from fastapi.responses import JSONResponse


class FeatureFlagController:
    def __init__(self, db: AsyncSession):
        self.service = FeatureFlagService(db)

    async def create(self, payload: FeatureFlagCreate) -> JSONResponse:
        request_id = str(uuid.uuid4())
        result = await self.service.create(payload.name, payload.enabled, request_id)
        return success_response(201, result, request_id)

    async def get(self, name: str) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.get(name, request_id)
            return success_response(200, result, request_id)
        except FeatureFlagNotFoundError as e:
            return error_response(404, str(e), request_id)

    async def list_all(self) -> JSONResponse:
        request_id = str(uuid.uuid4())
        result = await self.service.list_all(request_id)
        return success_response(200, result, request_id)

    async def toggle(self, name: str, payload: FeatureFlagUpdate) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.toggle(name, payload.enabled, request_id)
            return success_response(200, result, request_id)
        except FeatureFlagNotFoundError as e:
            return error_response(404, str(e), request_id)
