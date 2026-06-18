import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.utils.cache import redis_client
from app.utils.exceptions import UserNotFoundError

PERM_TTL = 900


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_user(self, user_id: str, request_id: str) -> dict:
        data = await self.repo.get_by_id(user_id)
        if not data:
            raise UserNotFoundError("User not found")
        return data

    async def list_users(self, request_id: str) -> list[dict]:
        users = await self.repo.get_all()
        return [
            {"user_id": u.user_id, "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active}
            for u in users
        ]

    async def update_user(self, user_id: str, is_active: bool | None, role: str | None, request_id: str) -> dict:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        print(f"Updating userzzzzzz, {user}")
        if is_active is not None:
            user["is_active"] = is_active
        if role is not None:
            user["role"] = role.value if hasattr(role, "value") else role
        print("after the user obj is updatesd",user)
        user = await self.repo.update(user)
        await redis_client.delete(f"rbac:user:{user_id}")
        await redis_client.delete(f"rbac:permissions:{user_id}")
        # return {"user_id": user.user_id, "username": user.username, "role": user.role, "is_active": user.is_active}
        return user
