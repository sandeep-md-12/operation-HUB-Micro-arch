from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.utils.auth import get_current_user
from app.schemas.job import JobCreate
from app.controllers.job_controller import JobController

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/csv")
async def submit_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await JobController(db).submit_csv(file, current_user["user_id"])


@router.post("/report")
async def submit_report(
    payload: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await JobController(db).submit_report(payload, current_user["user_id"])


@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await JobController(db).get_job(job_id, current_user)


@router.get("/")
async def list_jobs(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await JobController(db).list_jobs(current_user["user_id"])
