from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from app.utils.auth import require_admin
from app.schemas.audit_log import AuditLogCreate
from app.controllers.audit_log_controller import AuditLogController
import os

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])
controller = AuditLogController()

_INTERNAL_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN")


def _require_internal(x_internal_token: str = Header(None)):
    if not _INTERNAL_TOKEN or x_internal_token != _INTERNAL_TOKEN:
        raise HTTPException(status_code=403, detail="Internal access only")


@router.post("/")
async def create_log(payload: AuditLogCreate, _: None = Depends(_require_internal)):
    return await controller.create(payload)


@router.get("/")
async def query_logs(
    actor_id: Optional[str] = None,
    action_type: Optional[str] = None,
    module_source: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    _: dict = Depends(require_admin)
):
    return await controller.query(actor_id, action_type, module_source, start, end)
