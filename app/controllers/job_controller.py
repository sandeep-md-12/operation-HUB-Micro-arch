import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from app.services.job_service import JobService
from app.services.feature_flag_service import FeatureFlagService
from app.schemas.job import JobCreate
from app.models.job import JobType
from app.utils.response import success_response, error_response
from app.utils.exceptions import JobNotFoundError, FeatureDisabledError
from app.utils.s3 import upload_to_s3
from app.tasks.job_tasks import process_csv_task, generate_report_task
from fastapi.responses import JSONResponse

MAX_CSV_SIZE = 50 * 1024 * 1024  # 50MB


class JobController:
    def __init__(self, db: AsyncSession):
        self.service = JobService(db)
        self.flags = FeatureFlagService(db)

    async def submit_csv(self, file: UploadFile, actor_id: str) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            await self.flags.require_enabled("csv_import", request_id)
        except FeatureDisabledError as e:
            return error_response(403, str(e), request_id)
        s3_key = f"csv/{actor_id}/{request_id}/{file.filename}"
        chunks = []
        total = 0
        while chunk := await file.read(64 * 1024):
            total += len(chunk)
            if total > MAX_CSV_SIZE:
                raise HTTPException(status_code=413, detail="File too large. Max 50MB.")
            chunks.append(chunk)
        await upload_to_s3(s3_key, b"".join(chunks), "text/csv")
        job = await self.service.create_job(actor_id, JobType.csv_import, s3_key, None, request_id)
        process_csv_task.delay(job["job_id"], s3_key, actor_id)
        return success_response(201, job, request_id)

    async def submit_report(self, payload: JobCreate, actor_id: str) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            await self.flags.require_enabled("report_generation", request_id)
        except FeatureDisabledError as e:
            return error_response(403, str(e), request_id)
        job = await self.service.create_job(actor_id, JobType.report, None, payload.meta, request_id)
        generate_report_task.delay(job["job_id"], actor_id, payload.meta)
        return success_response(201, job, request_id)

    async def get_job(self, job_id: str, current_user: dict) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            result = await self.service.get_job(job_id, request_id)
            if result["actor_id"] != current_user["user_id"] and current_user["role"] != "Admin":
                return error_response(403, "Access denied", request_id)
            return success_response(200, result, request_id)
        except JobNotFoundError as e:
            return error_response(404, str(e), request_id)

    async def list_jobs(self, actor_id: str) -> JSONResponse:
        request_id = str(uuid.uuid4())
        result = await self.service.list_jobs(actor_id, request_id)
        return success_response(200, result, request_id)
