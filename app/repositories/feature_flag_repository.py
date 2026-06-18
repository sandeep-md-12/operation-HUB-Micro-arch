import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.feature_flag import FeatureFlag
from app.utils.cache import redis_client

FLAG_TTL = 900


class FeatureFlagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_dict(self, flag: FeatureFlag) -> dict:
        return {"name": flag.name, "enabled": flag.enabled}

    async def create(self, name: str, enabled: bool) -> FeatureFlag:
        flag = FeatureFlag(name=name, enabled=enabled)
        self.db.add(flag)
        await self.db.commit()
        await self.db.refresh(flag)
        await redis_client.delete(f"rbac:flag:{name}")
        return flag

    async def get_by_name(self, name: str) -> dict | None:
        cache_key = f"rbac:flag:{name}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        result = await self.db.execute(select(FeatureFlag).where(FeatureFlag.name == name))
        flag = result.scalar_one_or_none()
        if flag:
            data = self._to_dict(flag)
            await redis_client.setex(cache_key, FLAG_TTL, json.dumps(data))
            return data
        return None

    async def get_all(self) -> list[FeatureFlag]:
        result = await self.db.execute(select(FeatureFlag))
        return list(result.scalars().all())

    async def update(self, name: str, enabled: bool) -> dict | None:
        result = await self.db.execute(select(FeatureFlag).where(FeatureFlag.name == name))
        flag = result.scalar_one_or_none()
        if not flag:
            return None
        flag.enabled = enabled
        await self.db.commit()
        await self.db.refresh(flag)
        await redis_client.delete(f"rbac:flag:{name}")
        return self._to_dict(flag)
