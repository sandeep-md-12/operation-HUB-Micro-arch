import uuid
from datetime import datetime
from app.schemas.audit_log import AuditLogCreate
from app.services.audit_log_service import write_log, query_logs
from app.utils.response import success_response, error_response
from fastapi.responses import JSONResponse


class AuditLogController:
    async def create(self, payload: AuditLogCreate) -> JSONResponse:
        request_id = str(uuid.uuid4())
        try:
            item = payload.model_dump()
            item["timestamp"] = datetime.utcnow().isoformat()
            result = await write_log(item)
            return success_response(201, result, request_id)
        except Exception as e:
            return error_response(500, str(e), request_id)

    async def query(self, actor_id: str, action_type: str, module_source: str,
                    start: str, end: str) -> JSONResponse:
        request_id = str(uuid.uuid4())
        result = await query_logs(actor_id, action_type, module_source, start, end)
        return success_response(200, result, request_id)
