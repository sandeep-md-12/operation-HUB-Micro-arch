from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.feature_flag_repository import FeatureFlagRepository
from app.utils.exceptions import FeatureFlagNotFoundError, FeatureDisabledError


class FeatureFlagService:
    def __init__(self, db: AsyncSession):
        self.repo = FeatureFlagRepository(db)

    async def create(self, name: str, enabled: bool, request_id: str) -> dict:
        flag = await self.repo.create(name, enabled)
        return {"name": flag.name, "enabled": flag.enabled}

    async def get(self, name: str, request_id: str) -> dict:
        data = await self.repo.get_by_name(name)
        if not data:
            raise FeatureFlagNotFoundError(f"Feature flag '{name}' not found")
        return data

    async def require_enabled(self, name: str, request_id: str):
        try:
            flag = await self.get(name, request_id)
            if not flag["enabled"]:
                raise FeatureDisabledError(f"Feature '{name}' is currently disabled")
        except FeatureFlagNotFoundError:
            raise FeatureDisabledError(f"Feature '{name}' is currently disabled")

    async def list_all(self, request_id: str) -> list[dict]:
        flags = await self.repo.get_all()
        return [{"name": f.name, "enabled": f.enabled} for f in flags]

    async def toggle(self, name: str, enabled: bool, request_id: str) -> dict:
        data = await self.repo.update(name, enabled)
        if not data:
            raise FeatureFlagNotFoundError(f"Feature flag '{name}' not found")
        return data
