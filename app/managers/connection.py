from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from typing import Literal, Dict, Any, List, Union,Optional
from app.models.websocket import WebSocketMessage
from app.models.game import Game
from app.models.rule import Rule
from ..models.player import Player
import traceback


class ConnectionManager:
    def __init__(self,sokcets:List[WebSocket]=[],games:List[Game]=[]):
        self.active_connections: List[WebSocket] = sokcets
        self.games:List[Game]=games
        self.callbacked_connection:List[Dict[WebSocket,bool]]=[]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: WebSocketMessage, websocket: WebSocket):
        await websocket.send_json(message.model_dump())

    async def broadcast(self, message: WebSocketMessage):
        for connection in self.active_connections:
            await connection.send_json(message.model_dump())
    
    def create_game(self, websocket: WebSocket,rule:Rule=Rule()):
        last_game=self.get_game(websocket,True)
        new_game=Game(rule=rule,players=([Player(socket=websocket)]+[Player() for _ in range(3)]))
        new_game.qipai(other=last_game)
        self.games.append(new_game)
        self.callbacked_connection.append({websocket:False})
        return new_game
    
    def get_game(self, websocket: WebSocket,with_remove:bool=False):
        for game in self.games:
            for player in game.players:
                if player.socket == websocket:
                    self.games.remove(game) if with_remove else None
                    return game
        
        return None
    
    def callback(self,websocket:WebSocket,bool:bool=True):
        for s in self.callbacked_connection:
            if websocket in s:
                s[websocket]=bool
                return True
        return False
    
    def is_callbacked(self,game:Game):
        sockets=[p.socket for p in game.players if p.socket ]
        for s in sockets:
            found = False
            for connection in self.callbacked_connection:
                if s in connection:
                    if not connection[s]:
                        return False
                    found = True
                    break
            
            if not found:
                return False
        return True
    
    def reset_callback(self,game:Game):
        sockets=[p.socket for p in game.players if p.socket ]
        for s in sockets:
            self.callback(s,False)
            
    
