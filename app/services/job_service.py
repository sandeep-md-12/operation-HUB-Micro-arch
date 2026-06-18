import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job, JobType, JobState
from app.repositories.job_repository import JobRepository
from app.utils.cache import redis_client
from app.utils.exceptions import JobNotFoundError

REPORT_TTL = 3600


class JobService:
    def __init__(self, db: AsyncSession):
        self.repo = JobRepository(db)

    async def create_job(self, actor_id: str, job_type: JobType, s3_key: str | None, meta: dict | None, request_id: str) -> dict:
        job = Job(
            job_id=str(uuid.uuid4()),
            actor_id=actor_id,
            job_type=job_type,
            state=JobState.pending,
            s3_key=s3_key,
            meta=meta,
        )
        job = await self.repo.create(job)
        return self._to_dict(job)

    async def get_job(self, job_id: str, request_id: str) -> dict:
        cache_key = f"job:result:{job_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError("Job not found")
        return self._to_dict(job)

    async def list_jobs(self, actor_id: str, request_id: str) -> list[dict]:
        jobs = await self.repo.get_by_actor(actor_id)
        return [self._to_dict(j) for j in jobs]

    def _to_dict(self, job: Job) -> dict:
        return {
            "job_id": job.job_id,
            "actor_id": job.actor_id,
            "job_type": job.job_type,
            "state": job.state,
            "s3_key": job.s3_key,
            "result_s3_key": job.result_s3_key,
            "meta": job.meta,
        }
