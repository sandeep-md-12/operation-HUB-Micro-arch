from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.schemas.user import UserRegister, UserLogin
from app.controllers.auth_controller import AuthController

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    return await AuthController(db).register(payload)


@router.post("/login")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthController(db).login(payload)
