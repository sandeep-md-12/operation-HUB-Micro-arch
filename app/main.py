from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.database import init_db
from app.utils.dynamo import init_audit_log_table
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.job_routes import router as job_router
from app.routes.feature_flag_routes import router as feature_flag_router
from app.routes.notification_routes import router as notification_router
from app.routes.audit_log_routes import router as audit_log_router
from app.tasks.notification_tasks import listen_job_events

# just to push code 
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_audit_log_table()
    listen_job_events.delay()
    yield


app = FastAPI(title="Operations Hub", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(feature_flag_router)
app.include_router(job_router)
app.include_router(notification_router)
app.include_router(audit_log_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
