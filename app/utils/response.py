from fastapi.responses import JSONResponse


def success_response(code: int, data, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content={"status": "success", "code": code, "request_id": request_id, "data": data}
    )


def error_response(code: int, message: str, request_id: str = None) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content={"status": "error", "code": code, "request_id": request_id, "error": message}
    )
