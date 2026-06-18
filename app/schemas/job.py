from pydantic import BaseModel
from typing import Optional
from app.models.job import JobType, JobState


class JobCreate(BaseModel):
    job_type: JobType
    meta: Optional[dict] = None


class JobUpdate(BaseModel):
    state: Optional[JobState] = None
    result_s3_key: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    actor_id: str
    job_type: str
    state: str
    s3_key: Optional[str] = None
    result_s3_key: Optional[str] = None
    meta: Optional[dict] = None

    model_config = {"from_attributes": True}
