from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.utils.auth import get_current_user, require_admin
from app.schemas.notification import NotificationCreate
from app.controllers.notification_controller import NotificationController
from app.utils.websocket import manager

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/")
async def create_notification(payload: NotificationCreate, db: AsyncSession = Depends(get_db), _: dict = Depends(require_admin)):
    return await NotificationController(db).create(payload)


@router.get("/user/{recipient_id}")
async def list_for_user(recipient_id: str, unread: bool = False, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != recipient_id and current_user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return await NotificationController(db).list_for_user(recipient_id, unread)


@router.get("/{notification_id}")
async def get_notification(notification_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await NotificationController(db).get(notification_id, current_user)


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await NotificationController(db).mark_read(notification_id, current_user)


@router.websocket("/ws/{recipient_id}")
async def websocket_endpoint(recipient_id: str, websocket: WebSocket):
    await manager.connect(recipient_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(recipient_id)
