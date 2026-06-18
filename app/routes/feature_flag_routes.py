from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.utils.auth import get_current_user, require_admin
from app.schemas.feature_flag import FeatureFlagCreate, FeatureFlagUpdate
from app.controllers.feature_flag_controller import FeatureFlagController

router = APIRouter(prefix="/feature-flags", tags=["Feature Flags"])


@router.post("/")
async def create_flag(payload: FeatureFlagCreate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    return await FeatureFlagController(db).create(payload)


@router.get("/{name}")
async def get_flag(name: str, db: AsyncSession = Depends(get_db), _: dict = Depends(get_current_user)):
    return await FeatureFlagController(db).get(name)


@router.get("/")
async def list_flags(db: AsyncSession = Depends(get_db), _: dict = Depends(get_current_user)):
    return await FeatureFlagController(db).list_all()


@router.patch("/{name}")
async def toggle_flag(name: str, payload: FeatureFlagUpdate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    return await FeatureFlagController(db).toggle(name, payload)
