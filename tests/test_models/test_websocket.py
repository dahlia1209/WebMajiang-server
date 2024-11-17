from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.routers.websocket import router, get_connection_manager
from pydantic import BaseModel
from typing import Union, List
from app.models.websocket import GameState, ScoreContent, GameMessage, ScoreMessage
from app.models.pai import Pai
from app.models.shoupai import Fulou


def test_Websocket_init():
    game_state = GameState()
    score_content = ScoreContent()
    game_message = GameMessage(game=game_state)
    score_message = ScoreMessage(score=score_content)

    game_state = GameState(
        action="dapai",
        turn="duimian",
        status="ready",
        dapai=Pai(suit="p", num=1).serialize(),
        fulou=Fulou(type="peng").serialize(),
        canFulouList=[Fulou(type="chi").serialize() for _ in range(3)],
    )
    score_content = ScoreContent(
        baopai=[Pai(suit="p", num=1).serialize() for _ in range(5)],
        zhuangfeng="西",
        menfeng="西",
        jushu=8,
        jicun=3,
        changbang=10,
        defen=[10000, 20000, 30000, 40000],
    )
    game_message = GameMessage(game=game_state)
    score_message = ScoreMessage(score=score_content)
