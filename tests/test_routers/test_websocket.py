from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.routers.websocket import router,SimpleMessage,GameMessage,GameState,get_connection_manager,WebSocketMessageHandler,ScoreMessage
import json
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Union,List
from app.models.type import Position
from app.models.pai import Pai
from app.managers.connection import ConnectionManager

app = FastAPI()
app.include_router(router)
client=TestClient(app)
con_mgr = ConnectionManager()

def override_dependency():
    return con_mgr

app.dependency_overrides[get_connection_manager]=override_dependency

def test_websocket_handler():
    
    def zimo_handler(game_msg:GameMessage)->str:
        print("zimo_handler",game_msg)
        if(game_msg.game.action!="zimo"):
            raise ValueError((f"正しいアクションを指定してください。与えられたアクション:{game_msg.game.action}"))
        
        if game_msg.game.status=="thinking":
            # zimo thinking
            assert game_msg.game.canFulouList ==[]
            assert game_msg.game.fulou is None
            assert game_msg.game.dapai is None
            assert game_msg.game.qipai is None
            assert game_msg.game.status =="thinking"
            # first_turn=["main","xiajia","duimian","shangjia"][["東", "北","西","南"].index(score_msg.score.menfeng)]
            assert game_msg.game.turn in ["main","xiajia","duimian","shangjia"]
            zimopai=game_msg.game.zimopai
            assert zimopai!="b0" if game_msg.game.turn=="main" else zimopai =="b0"
            m=GameMessage(type="game",game=GameState(action="zimo",status="ready"))
            websocket.send_json(m.model_dump())
            return zimopai
        else :
            raise ValueError((f"zimoのreadyは受信しないっす"))
        
    
    def dapai_handler(game_msg:GameMessage,zimo:str)->str:
        print("dapai_handler",game_msg)
        if(game_msg.game.action!="dapai"):
            raise ValueError((f"正しいアクションを指定してください。与えられたアクション:{game_msg.game.action}"))
        if game_msg.game.status=="thinking":
            assert game_msg.game.dapai is None
            assert game_msg.game.turn in ["main","xiajia","duimian","shangjia"]
            assert game_msg.game.zimopai is None
            if game_msg.game.turn =="main":
                m=GameMessage(type="game",game=GameState(action="dapai",status="ready",turn="main",dapai=zimo))
                websocket.send_json(m.model_dump())
                return zimo
            else :
                res = websocket.receive_json()
                game_msg=GameMessage(**res)
                zimo=dapai_handler(game_msg,zimo)
                return zimo
                
        else:
            assert game_msg.game.dapai[0] in ["m", "p", "s", "z"]
            assert int(game_msg.game.dapai[1]) in range(1,10)
            assert game_msg.game.dapai[2] in ["t","f"]
            assert game_msg.game.turn in ["xiajia","duimian","shangjia"]
            assert game_msg.game.zimopai is None
            m=GameMessage(type="game",game=GameState(action="dapai",status="ready"))
            websocket.send_json(m.model_dump())
            return game_msg.game.dapai
    
    
    for _ in range(3):
        with client.websocket_connect("/ws") as websocket:
            #開局、配牌
            m=GameMessage(type="game",game=GameState(action="kaiju"))
            websocket.send_json(m.model_dump())
            res = websocket.receive_json()
            score_msg=ScoreMessage(**res)
            assert len(score_msg.score.baopai)==5
            assert score_msg.score.baopai[0]!="b0f"
            assert [score_msg.score.baopai[i]=="b0f" for i in range(1,5)]
            assert score_msg.score.changbang==0
            assert score_msg.score.defen==[25000,25000,25000,25000]
            assert score_msg.score.jushu==1
            assert score_msg.score.jicun==0
            assert score_msg.score.menfeng in ["東", "南", "西", "北"]
            assert score_msg.score.zhuangfeng == "東"
            res = websocket.receive_json()
            game_msg=GameMessage(**res)
            assert game_msg.game.action=="kaiju"
            assert game_msg.game.canFulouList ==[]
            assert game_msg.game.fulou is None
            assert game_msg.game.dapai is None
            assert game_msg.game.turn is None
            assert game_msg.game.zimopai is None
            assert game_msg.game.status is None
            assert len(game_msg.game.qipai.split("+"))==13
            
            #17巡ツモ＆ツモ切り
            for _ in range(17):
                for _ in range(4):
                    res=None
                    res = websocket.receive_json()
                    game_msg=GameMessage(**res)
                    zimo=zimo_handler(game_msg)
                    res=None
                    res = websocket.receive_json()
                    game_msg=GameMessage(**res)
                    dapai=dapai_handler(game_msg,zimo)
            
            #ラスト2牌
            for _ in range(2):
                    res=None
                    res = websocket.receive_json()
                    game_msg=GameMessage(**res)
                    zimo=zimo_handler(game_msg)
                    res=None
                    res = websocket.receive_json()
                    game_msg=GameMessage(**res)
                    dapai=dapai_handler(game_msg,zimo)
            
            websocket.close()

            
        
