from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job: Job) -> Job:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: str) -> Job | None:
        result = await self.db.execute(select(Job).where(Job.job_id == job_id))
        return result.scalar_one_or_none()

    async def update(self, job: Job) -> Job:
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_by_actor(self, actor_id: str) -> list[Job]:
        result = await self.db.execute(select(Job).where(Job.actor_id == actor_id))
        return list(result.scalars().all())
