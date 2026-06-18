import os
from celery import Celery
from dotenv import load_dotenv
from celery.signals import worker_process_init
# Import your global SQLAlchemy engine here
from app.utils.database import engine

load_dotenv()

celery_app = Celery(
    __name__,
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

@worker_process_init.connect
def dispose_database_engine(**kwargs):
    """
    This forces every newly forked Celery worker to destroy the broken 
    connection pool it inherited and create a fresh one.
    """
    # For async engines, you must use the sync_engine to dispose
    engine.sync_engine.dispose()
# celery_app.autodiscover_tasks(['app.tasks'])
celery_app.conf.imports = ("app.tasks.job_tasks", "app.tasks.notification_tasks")

# celery_app.autodiscover_tasks(["app"], related_name="tasks.job_tasks")