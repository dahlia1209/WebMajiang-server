from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.routers.websocket import router,SimpleMessage,GameMessage,GameState,WebSocketMessageHandler,ScoreMessage,get_websocket_handler_manager
import json
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Union,List
from app.models.type import Position
from app.models.pai import Pai
from app.managers.connection import ConnectionManager
from app.models.game import Game,Hupai
from app.models.player import Player
from app.models.shoupai import Fulou
import pytest

# app = FastAPI()
# app.include_router(router)
# client=TestClient(app)
# handler = WebSocketMessageHandler()

# def override_dependency():
#     return handler

# app.dependency_overrides[get_websocket_handler_manager]=override_dependency

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def handler():
    return WebSocketMessageHandler()

@pytest.fixture
def client(app, handler):
    app.dependency_overrides[get_websocket_handler_manager] = lambda: handler
    return TestClient(app)

def test_handler(client, handler):
    #シングルトンの確認
    handler_2=WebSocketMessageHandler()
    assert handler_2==handler
    assert len(handler.manager.active_connections)==0
    with client.websocket_connect("/ws") as websocket:
        #ハンドラーの依存性注入の確認
        m=GameMessage(type="game",game=GameState(action="kaiju"))
        websocket.send_json(m.model_dump())
        #接続数が1
        assert len(handler.manager.active_connections)==1 
        res = websocket.receive_json()
        #ゲーム数が1
        assert len(handler.games)==1
        #ボット3人、プレイヤーが1人
        assert sum([p.is_bot() for i,p in enumerate(handler.games[0].players)])==3
        assert sum([not p.is_bot() for i,p in enumerate(handler.games[0].players)])==1
        # print("handler.games[0].model_dump_json()",handler.games[0].players[0].model_dump_json(exclude={'socket'}))


def test_websocket_handler(client, handler):
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
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="qipai"
                # assert game_msg.game.fulouCandidates ==[]
                assert recieved_game_msg.game.fulou is None
                assert recieved_game_msg.game.dapai is None
                assert recieved_game_msg.game.turn is None
                assert recieved_game_msg.game.zimopai is None
                # assert game_msg.game.status is None
                assert len(recieved_game_msg.game.qipai.split("+"))==13
                m=GameMessage(type="game",game=GameState(action="qipai"))
                websocket.send_json(m.model_dump())
                
                
                #17巡ツモ＆ツモ切り
                for _ in range(17):
                    for _ in range(4):
                        res=None
                        res = websocket.receive_json()
                        recieved_game_msg=GameMessage(**res)
                        assert recieved_game_msg.game.action =="zimo"
                        if recieved_game_msg.game.turn =="main":
                            assert recieved_game_msg.game.zimopai is not None and recieved_game_msg.game.zimopai!="b0"
                            client_msg=GameMessage(game=GameState(action="zimo",dapai=",".join([recieved_game_msg.game.zimopai,"99"])))
                            websocket.send_json(client_msg.model_dump())
                        else:
                            assert recieved_game_msg.game.zimopai is not None and recieved_game_msg.game.zimopai=="b0"
                            client_msg=GameMessage(game=GameState(action="zimo"))
                            websocket.send_json(client_msg.model_dump())
                        res = websocket.receive_json()
                        recieved_game_msg=GameMessage(**res)
                        assert recieved_game_msg.game.action =="dapai"
                        assert recieved_game_msg.game.dapai is not None and recieved_game_msg.game.dapai!="b0"
                        client_msg=GameMessage(game=GameState(action="dapai"))
                        websocket.send_json(client_msg.model_dump())
                        
                
                #ラスト2牌
                for _ in range(2):
                    res=None
                    res = websocket.receive_json()
                    recieved_game_msg=GameMessage(**res)
                    assert recieved_game_msg.game.action =="zimo"
                    if recieved_game_msg.game.turn =="main":
                        assert recieved_game_msg.game.zimopai is not None and recieved_game_msg.game.zimopai!="b0"
                        client_msg=GameMessage(game=GameState(action="zimo",dapai=",".join([recieved_game_msg.game.zimopai,"99"])))
                        websocket.send_json(client_msg.model_dump())
                    else:
                        assert recieved_game_msg.game.zimopai is not None and recieved_game_msg.game.zimopai=="b0"
                        client_msg=GameMessage(game=GameState(action="zimo"))
                        websocket.send_json(client_msg.model_dump())
                    res = websocket.receive_json()
                    recieved_game_msg=GameMessage(**res)
                    assert recieved_game_msg.game.action =="dapai"
                    assert recieved_game_msg.game.dapai is not None and recieved_game_msg.game.dapai!="b0"
                    client_msg=GameMessage(game=GameState(action="dapai"))
                    websocket.send_json(client_msg.model_dump())
                
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action =="pingju"
                client_msg=GameMessage(game=GameState(action="pingju"))
                websocket.send_json(client_msg.model_dump())
            
            res = websocket.receive_json()
            recieved_game_msg=GameMessage(**res)
            assert recieved_game_msg.game.action =="jieju"
            
            websocket.close()

def test_lizhi(client, handler):
    with client.websocket_connect("/ws") as websocket:
        #開局、配牌
        m=GameMessage(type="game",game=GameState(action="kaiju"))
        websocket.send_json(m.model_dump())
        res = websocket.receive_json()
        score_msg=ScoreMessage(**res)
        first_mengfeng=score_msg.score.menfeng
        res = websocket.receive_json()
        recieved_game_msg=GameMessage(**res)
        m=GameMessage(type="game",game=GameState(action="qipai"))
        websocket.send_json(m.model_dump())
        
        bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p3","p4"]]
        player_id,player=next((i,p) for i,p in enumerate(handler.games[0].players) if not  p.is_bot())
        player.shoupai.bingpai=bingpai
        player.shoupai._compute_xiangting()
        assert handler.games[0].players[player_id].shoupai.bingpai==bingpai
        assert player.shoupai.xiangting==0
        #1巡ツモ切り
        for i in range(4):
            res=None
            res = websocket.receive_json()
            recieved_game_msg=GameMessage(**res)
            if recieved_game_msg.game.turn =="main":
                assert player_id==i
                assert recieved_game_msg.game.action=="zimo"
                lizhipai=recieved_game_msg.game.zimopai
                client_msg=GameMessage(game=GameState(action="zimo",dapai=",".join([lizhipai,"99"]),lizhipai=lizhipai))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="lizhi"
                assert recieved_game_msg.game.dapai==",".join([lizhipai,"99"])
                
                assert player.shoupai.xiangting==0
                assert player.shoupai.is_yifa
                assert player.shoupai.lizhi_flag==2
                client_msg=GameMessage(game=GameState(action="lizhi"))
                websocket.send_json(client_msg.model_dump())
            else:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai"))
                websocket.send_json(client_msg.model_dump())
        #2巡ツモアガリ
        for i in range(4):
            res=None
            res = websocket.receive_json()
            recieved_game_msg=GameMessage(**res)
            if recieved_game_msg.game.turn =="main":
                assert player_id==i
                assert recieved_game_msg.game.action=="zimo"
                assert recieved_game_msg.game.hule=="+".join(["p2f","p5f"])
                client_msg=GameMessage(game=GameState(action="zimo",turn="main",hule="p5f"))
                websocket.send_json(client_msg.model_dump())
                
                break
            else:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="dapai"
                assert recieved_game_msg.game.hule in ["p2f+p5f","p2f+p5f+b0"]
                client_msg=GameMessage(game=GameState(action="dapai"))
                websocket.send_json(client_msg.model_dump())
        
        res=None
        res = websocket.receive_json()
        recieved_game_msg=GameMessage(**res)
        assert recieved_game_msg.game.action=="hule"
        assert recieved_game_msg.game.turn=="main"
        client_msg=GameMessage(game=GameState(action="hule",turn="main"))
        websocket.send_json(client_msg.model_dump())
        res = websocket.receive_json()
        score_msg=ScoreMessage(**res)
        assert handler.games[0].score.defen!=[25000, 25000, 25000, 25000]
        assert score_msg.score.defen !=[25000, 25000, 25000, 25000]
        assert score_msg.score.defen[player_id]>25000
        assert score_msg.score.menfeng==handler.games[0].get_next_feng(first_mengfeng)
        res = websocket.receive_json()
        recieved_game_msg=GameMessage(**res)
        assert recieved_game_msg.game.action=="qipai"
        
def test_gang(client, handler):
    with client.websocket_connect("/ws") as websocket:
        #開局、配牌
        m=GameMessage(type="game",game=GameState(action="kaiju"))
        websocket.send_json(m.model_dump())
        res = websocket.receive_json()
        score_msg=ScoreMessage(**res)
        first_mengfeng=score_msg.score.menfeng
        res = websocket.receive_json()
        recieved_game_msg=GameMessage(**res)
        m=GameMessage(type="game",game=GameState(action="qipai"))
        websocket.send_json(m.model_dump())
        
        bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m1","m2","m2","m2","p4","p5","p5","z7","z7","z7"]]
        player_id,player=next((i,p) for i,p in enumerate(handler.games[0].players) if not  p.is_bot())
        player.shoupai.bingpai=bingpai
        player.shoupai._compute_xiangting()
        bot_id,bot_player=next((i,p) for i,p in enumerate(handler.games[0].players) if  p.is_bot())
        #1巡目暗槓・嶺上ツモ・ツモ切り
        for i in range(4):
            res=None
            res = websocket.receive_json()
            recieved_game_msg=GameMessage(**res)
            if player_id ==i:
                fulou_candidates=[Fulou.deserialize(s) for s in recieved_game_msg.game.fulouCandidates.split("|")]
                assert fulou_candidates[0].serialize()=="angang,null,m1f+m1f+m1f+m1f,null"
                client_msg=GameMessage(game=GameState(action="zimo",fulou=fulou_candidates[0].serialize(),turn="main"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="fulou"
                assert recieved_game_msg.game.fulou==fulou_candidates[0].serialize()
                client_msg=GameMessage(game=GameState(action="fulou",turn="main",zimopai="b0"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="zimo"
                assert recieved_game_msg.game.zimopai is not None
                assert recieved_game_msg.game.baopai is not None
                assert handler.games[0].wangpai.baopai[1].serialize()==recieved_game_msg.game.baopai
                client_msg=GameMessage(game=GameState(action="zimo",turn="main",dapai=f"{recieved_game_msg.game.zimopai},99"))
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai",turn="main"))
                websocket.send_json(client_msg.model_dump())
                assert len(player.shoupai.bingpai)==10
            else:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai"))
                websocket.send_json(client_msg.model_dump())
        #2巡目明槓・嶺上ツモ・ツモ切り
        handler.games[0].shan.pais=[Pai.deserialize(s) for s in ["m2","m2","m2","m2"]]
        for i in range(4):
            res=None
            res = websocket.receive_json()
            recieved_game_msg=GameMessage(**res)
            if bot_id ==i:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.dapai=='m2f,99'
                fulou=f"minggang,m2,m2+m2+m2,duimian"
                client_msg=GameMessage(game=GameState(action="dapai",turn="main",fulou=fulou))
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="fulou"
                assert recieved_game_msg.game.fulou==fulou
                client_msg=GameMessage(game=GameState(action="fulou",turn="main",zimopai="b0"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="zimo"
                assert recieved_game_msg.game.zimopai is not None
                assert recieved_game_msg.game.baopai is not None
                assert handler.games[0].wangpai.baopai[2].serialize()==recieved_game_msg.game.baopai
                client_msg=GameMessage(game=GameState(action="zimo",turn="main",dapai=f"{recieved_game_msg.game.zimopai},99"))
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai",turn="main"))
                websocket.send_json(client_msg.model_dump())
                assert len(player.shoupai.bingpai)==7
            else:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai"))
                websocket.send_json(client_msg.model_dump())
        #3巡目ポン・加槓・嶺上ツモ・ツモ切り
        handler.games[0].shan.pais=[Pai.deserialize(s) for s in ["z7","z7","z7","z7"]]
        for i in range(4):
            res=None
            res = websocket.receive_json()
            recieved_game_msg=GameMessage(**res)
            if bot_id ==i:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.dapai=='z7f,99'
                fulou=f"peng,z7,z7+z7,shangjia"
                client_msg=GameMessage(game=GameState(action="dapai",turn="main",fulou=fulou))
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="fulou"
                assert recieved_game_msg.game.fulou==fulou
                fulou=f"jiagang,z7,z7+z7,shangjia"
                client_msg=GameMessage(game=GameState(action="fulou",turn="main",fulou=fulou))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="fulou"
                assert recieved_game_msg.game.fulou==fulou
                client_msg=GameMessage(game=GameState(action="fulou",turn="main",zimopai="b0"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                assert recieved_game_msg.game.action=="zimo"
                assert recieved_game_msg.game.zimopai is not None
                assert recieved_game_msg.game.baopai is not None
                assert handler.games[0].wangpai.baopai[3].serialize()==recieved_game_msg.game.baopai
                client_msg=GameMessage(game=GameState(action="zimo",turn="main",dapai=f"{recieved_game_msg.game.zimopai},99"))
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai",turn="main"))
                websocket.send_json(client_msg.model_dump())
                assert len(player.shoupai.bingpai)==4
            else:
                client_msg=GameMessage(game=GameState(action="zimo"))
                print("client_game_msg",client_msg)
                websocket.send_json(client_msg.model_dump())
                res = websocket.receive_json()
                recieved_game_msg=GameMessage(**res)
                client_msg=GameMessage(game=GameState(action="dapai"))
                websocket.send_json(client_msg.model_dump())
        