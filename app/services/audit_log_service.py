from app.repositories.audit_log_repository import AuditLogRepository

_repo = AuditLogRepository()


async def write_log(item: dict) -> dict:
    return await _repo.write(item)


async def query_logs(actor_id: str = None, action_type: str = None, module_source: str = None,
                     start: str = None, end: str = None) -> list[dict]:
    if actor_id:
        results = await _repo.query_by_actor(actor_id, start, end)
    elif action_type:
        results = await _repo.query_by_action_type(action_type, start, end)
    elif module_source:
        results = await _repo.query_by_module_source(module_source, start, end)
    else:
        return []

    if action_type and actor_id:
        results = [r for r in results if r.get("action_type") == action_type]
    if module_source and (actor_id or action_type):
        results = [r for r in results if r.get("module_source") == module_source]

    return results
