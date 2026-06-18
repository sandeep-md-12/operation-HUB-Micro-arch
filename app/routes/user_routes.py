from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.utils.auth import require_admin
from app.schemas.user import UserUpdate
from app.controllers.user_controller import UserController

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    return await UserController(db).get_user(user_id)


@router.get("/")
async def list_users(db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    return await UserController(db).list_users()


@router.patch("/{user_id}")
async def update_user(user_id: str, payload: UserUpdate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    return await UserController(db).update_user(user_id, payload)
