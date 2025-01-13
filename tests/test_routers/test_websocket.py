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
    for _ in range(1):
        with client.websocket_connect("/ws") as websocket:
            #開局、配牌
            m=GameMessage(type="game",game=GameState(action="kaiju"))
            websocket.send_json(m.model_dump())
            
            #半荘
            for jushu in range(1,9):
                res = websocket.receive_json()
                score_msg=ScoreMessage(**res)
                assert len(score_msg.score.baopai)==5
                assert score_msg.score.baopai[0]!="b0f"
                assert [score_msg.score.baopai[i]=="b0f" for i in range(1,5)]
                assert score_msg.score.changbang==0
                assert score_msg.score.defen==[25000,25000,25000,25000]
                assert score_msg.score.jushu==jushu
                assert score_msg.score.jicun==0
                assert score_msg.score.menfeng in ["東", "南", "西", "北"]
                if 1<=jushu<=4:
                    assert score_msg.score.zhuangfeng == "東" 
                elif 5<=jushu<=8:
                    assert score_msg.score.zhuangfeng == "南" 
                res = websocket.receive_json()
                game_msg=GameMessage(**res)
                assert game_msg.game.action=="qipai"
                # assert game_msg.game.fulouCandidates ==[]
                assert game_msg.game.fulou is None
                assert game_msg.game.dapai is None
                assert game_msg.game.turn is None
                assert game_msg.game.zimopai is None
                # assert game_msg.game.status is None
                assert len(game_msg.game.qipai.split("+"))==13
                m=GameMessage(type="game",game=GameState(action="qipai"))
                websocket.send_json(m.model_dump())
                
                
                #17巡ツモ＆ツモ切り
                for _ in range(17):
                    for _ in range(4):
                        res=None
                        res = websocket.receive_json()
                        game_msg=GameMessage(**res)
                        assert game_msg.game.action =="zimo"
                        if game_msg.game.turn =="main":
                            assert game_msg.game.zimopai is not None and game_msg.game.zimopai!="b0"
                            game_msg.game.dapai=",".join([game_msg.game.zimopai,"99"])
                            game_msg.game.zimopai=None
                            websocket.send_json(game_msg.model_dump())
                        else:
                            assert game_msg.game.zimopai is not None and game_msg.game.zimopai=="b0"
                            game_msg.game.zimopai=None
                            websocket.send_json(game_msg.model_dump())
                        res = websocket.receive_json()
                        game_msg=GameMessage(**res)
                        assert game_msg.game.action =="dapai"
                        assert game_msg.game.dapai is not None and game_msg.game.dapai!="b0"
                        game_msg.game.dapai=None
                        websocket.send_json(game_msg.model_dump())
                        
                
                #ラスト2牌
                for _ in range(2):
                    res=None
                    res = websocket.receive_json()
                    game_msg=GameMessage(**res)
                    assert game_msg.game.action =="zimo"
                    if game_msg.game.turn =="main":
                        assert game_msg.game.zimopai is not None and game_msg.game.zimopai!="b0"
                        game_msg.game.dapai=",".join([game_msg.game.zimopai,"99"])
                        game_msg.game.zimopai=None
                        websocket.send_json(game_msg.model_dump())
                    else:
                        assert game_msg.game.zimopai is not None and game_msg.game.zimopai=="b0"
                        game_msg.game.zimopai=None
                        websocket.send_json(game_msg.model_dump())
                    res = websocket.receive_json()
                    game_msg=GameMessage(**res)
                    assert game_msg.game.action =="dapai"
                    assert game_msg.game.dapai is not None and game_msg.game.dapai!="b0"
                    game_msg.game.dapai=None
                    websocket.send_json(game_msg.model_dump())
                
                res = websocket.receive_json()
                game_msg=GameMessage(**res)
                assert game_msg.game.action =="pingju"
                websocket.send_json(game_msg.model_dump())
            
            res = websocket.receive_json()
            game_msg=GameMessage(**res)
            assert game_msg.game.action =="jieju"
            
            websocket.close()



            
        
