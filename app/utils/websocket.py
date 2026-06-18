from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, recipient_id: str, websocket: WebSocket):
        await websocket.accept()
        self._connections[recipient_id] = websocket

    def disconnect(self, recipient_id: str):
        self._connections.pop(recipient_id, None)

    async def push(self, recipient_id: str, data: dict):
        ws = self._connections.get(recipient_id)
        if ws:
            await ws.send_json(data)


manager = ConnectionManager()
