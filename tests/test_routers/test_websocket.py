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


# @app.websocket("/ws")
# async def websocket(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_json({"msg": "Hello WebSocket"})
#     await websocket.close()

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []



def test_websocket():
    
    with client.websocket_connect("/ws") as websocket:
        m=SimpleMessage(msg="Hello world")
        websocket.send_json(m.model_dump())
        res = websocket.receive_json()
        res_m=SimpleMessage(**res)
        assert res_m.model_dump() == {"type":"message","msg":"Hello world"}