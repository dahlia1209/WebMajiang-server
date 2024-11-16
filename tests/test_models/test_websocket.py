from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.routers.websocket import router,get_connection_manager
import json
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Union,List
from app.managers.connection import ConnectionManager
from app.routers.websocket import SimpleMessage


app = FastAPI()
app.include_router(router)
client=TestClient(app)
