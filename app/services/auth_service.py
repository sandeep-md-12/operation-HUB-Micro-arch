import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.cache import redis_client
from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError, InactiveUserError

PERM_TTL = 900

    
class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, username: str, email: str, password: str, role: str, request_id: str) -> dict:
        if await self.repo.get_by_username(username):
            raise UserAlreadyExistsError("Username already taken")
        if await self.repo.get_by_email(email):
            raise UserAlreadyExistsError("Email already registered")
        user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )
        user = await self.repo.create(user)
        return {"user_id": user.user_id, "username": user.username, "role": user.role}

    async def login(self, username: str, password: str, request_id: str) -> dict:
        user = await self.repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsError("Invalid credentials")
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid credentials")
        if not user.is_active:
            raise InactiveUserError("Account is inactive")
        token = create_access_token(user.user_id, user.role)
        await redis_client.setex(
            f"rbac:permissions:{user.user_id}", PERM_TTL,
            json.dumps({"user_id": user.user_id, "role": user.role, "email": user.email})
        )
        return {"access_token": token, "token_type": "bearer"}
