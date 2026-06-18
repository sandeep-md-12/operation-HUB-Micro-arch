from pydantic import BaseModel
from typing import Optional


class AuditLogCreate(BaseModel):
    request_id: str
    actor_id: str
    action_type: str
    module_source: str
    source_ip: str
    payload: Optional[dict] = None


class AuditLogResponse(BaseModel):
    request_id: str
    timestamp: str
    actor_id: str
    action_type: str
    module_source: str
    source_ip: str
    payload: Optional[dict] = None

    model_config = {"from_attributes": True}
