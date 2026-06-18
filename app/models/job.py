import enum
from sqlalchemy import Column, String, Enum, JSON
from app.utils.database import Base


class JobType(str, enum.Enum):
    csv_import = "csv_import"
    report = "report"


class JobState(str, enum.Enum):
    pending = "Pending"
    running = "Running"
    completed = "Completed"
    failed = "Failed"
    retried = "Retried"


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    actor_id = Column(String, nullable=False)
    job_type = Column(Enum(JobType), nullable=False)
    state = Column(Enum(JobState), default=JobState.pending, nullable=False)
    s3_key = Column(String, nullable=True)
    result_s3_key = Column(String, nullable=True)
    meta = Column(JSON, nullable=True)

    def __eq__(self, other):
        return isinstance(other, Job) and self.job_id == other.job_id

    def __hash__(self):
        return hash(self.job_id)

    def __str__(self):
        return f"Job({self.job_id}, {self.job_type}, {self.state})"

    def __repr__(self):
        return self.__str__()
