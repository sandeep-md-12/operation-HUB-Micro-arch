import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy import select
from app.models.user import User
from app.utils.cache import redis_client

PERM_TTL = 900


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_dict(self, user) -> dict:
        if not user:
            return {}
            
        #  If 'user' is already a dictionary, skip dot-notation and return it safely!
        if isinstance(user, dict):
            return {
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "role": user.get("role"),
                "is_active": user.get("is_active")
            }
            
        # Otherwise, treat it like a database model object
        return {
            "user_id": getattr(user, "user_id", None),
            "username": getattr(user, "username", None),
            "email": getattr(user, "email", None),
            "role": getattr(user, "role", None),
            "is_active": getattr(user, "is_active", None)
        }
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> dict | None:
        cache_key = f"rbac:user:{user_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            data = self._to_dict(user)
            await redis_client.setex(cache_key, PERM_TTL, json.dumps(data))
            return data
        return None

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self.db.execute(select(User))
        return list(result.scalars().all())

    async def update(self, user: User) -> User:
        user_dict = self._to_dict(user)
        query = (
        sqlalchemy_update(User)
        .where(User.user_id == user_dict["user_id"])
        .values(
            is_active=user_dict["is_active"],
            role=user_dict["role"]
        )
        )
        await self.db.execute(query)
        await self.db.commit()
        return user_dict
