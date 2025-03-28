from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from typing import Literal, Dict, Any, List, Union,Optional
from app.models.websocket import WebSocketMessage
from app.models.game import Game
from app.models.websocket import SimpleMessage
from app.models.rule import Rule
from ..models.player import Player
import traceback
import random
from threading import local,Lock


class ConnectionManager:
    _instance: Optional['ConnectionManager'] = None
    _lock = Lock()
    active_connections:List[WebSocket]=[]
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock: 
                if cls._instance is None: 
                    cls._instance = super().__new__(cls)
                    # シングルトンの初期化
                    cls._instance.active_connections = []
        return cls._instance
    
    def __init__(self,sokcets:List[WebSocket]=[],games:List[Game]=[]):
        # self.active_connections: List[WebSocket] = sokcets
        pass

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        simpleMessage=SimpleMessage(type="message",msg="websocket connection opened")
        await websocket.send_json(simpleMessage.model_dump())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: WebSocketMessage, websocket: WebSocket):
        await websocket.send_json(message.model_dump())

    async def broadcast(self, message: WebSocketMessage):
        for connection in self.active_connections:
            await connection.send_json(message.model_dump())
