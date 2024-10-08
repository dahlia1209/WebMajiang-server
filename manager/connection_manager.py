from typing import List, Dict, Any,Optional,Literal,Union
from pydantic import BaseModel
from fastapi import WebSocket
from models.models import WsMessage

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: WsMessage, websocket: WebSocket):
        await websocket.send_text(message.model_dump_json())

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# manager = ConnectionManager()
