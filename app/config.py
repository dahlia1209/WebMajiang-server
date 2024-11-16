from pydantic_settings import BaseSettings
from .models.websocket import WebSocketModel
from typing import List

class Store(BaseSettings):
    sockets: List[WebSocketModel] =[]