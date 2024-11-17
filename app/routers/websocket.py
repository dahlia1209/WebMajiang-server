from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    WebSocketException,
    status,
)
from pydantic import BaseModel, ValidationError
from typing import Literal, Dict, Any, List, Union, Annotated,Optional
import json
from ..managers.connection import ConnectionManager
from ..models.pai import Pai
from ..models.game import Game
from ..models.websocket import (
    SimpleMessage,
    BaseMessage,
    GameMessage,
    GameState,
    ScoreContent,
    ScoreMessage,
)
from functools import lru_cache
from fastapi.encoders import jsonable_encoder
import traceback

router = APIRouter()
con_mgr = ConnectionManager()

def get_connection_manager():
    return con_mgr


class WebSocketMessageHandler:
    def __init__(self, websocket: WebSocket, connection_manager: ConnectionManager):
        self.websocket = websocket
        self.manager = connection_manager

    async def handle_message(self, message_data: dict) -> None:
        """メインのメッセージハンドリングフロー"""
        base_message = BaseMessage(**message_data)

        handlers = {
            "message": self._handle_simple_message,
            "game": self._handle_game_message,
        }

        handler = handlers.get(base_message.type)
        if not handler:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"不正なメッセージタイプ: {message_data}",
            )

        await handler(message_data)

    async def _handle_simple_message(self, data: dict) -> None:
        """シンプルメッセージの処理"""
        message = SimpleMessage(**data)
        await self.websocket.send_json(message.model_dump())

    async def _handle_game_message(self, data: dict) -> None:
        """ゲームメッセージの処理"""
        message = GameMessage(**data)

        handlers = {
            "kaiju": self._handle_game_start,
            "zimo": self._handle_zimo,
            "dapai": self._handle_dapai,
        }

        handler = handlers.get(message.game.action)
        if not handler:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"不正なゲームアクション: {data}",
            )

        await handler(message)

    async def _handle_game_start(self, message: GameMessage) -> None:
        """開局処理"""
        new_game = self.manager.create_game(websocket=self.websocket)
        result = self.manager.callback(self.websocket)
        if self.manager.is_callbacked(new_game):
            await self._send_initial_game_state(new_game)
            await self._send_zimo(new_game)
            self.manager.reset_callback(new_game)

    async def _send_initial_game_state(self, game: Game) -> None:
        """初期状態の送信"""
        qipai_msg = GameMessage(type="game", game=GameState(action="kaiju"))

        for i in range(4):
            if game.players[i].socket:
                await self._send_player_initial_state(game, i, qipai_msg)

    async def _send_player_initial_state(
        self, game: Game, player_index: int, qipai_msg: GameMessage
    ) -> None:
        """各プレイヤーへの初期状態送信"""
        score_msg = ScoreMessage(
            score=ScoreContent(
                baopai=[p.serialize() for p in game.score.baopai],
                menfeng=game.score.menfeng[player_index],
            )
        )

        await self.manager.send_personal_message(
            score_msg, game.players[player_index].socket
        )

        qipai_msg.game.qipai = "+".join(
            sorted([p.serialize() for p in game.players[player_index].shoupai.bingpai])
        )
        await self.manager.send_personal_message(
            qipai_msg, game.players[player_index].socket
        )

    async def _send_zimo(self, game: Game) -> None:
        """ツモ牌送信"""
        for i in range(4):
            zimo_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="zimo",
                        turn=game.get_turn(i),
                        status="thinking",
                        zimopai="b0"
                    ),
                )
            if game.players[i].menfeng==game.teban:
                zimopai=game.zimo(i)
                zimo_msg.game.zimopai=zimopai.serialize()
            if game.players[i].socket:
                await self.manager.send_personal_message(zimo_msg, game.players[i].socket)
        
    async def _handle_zimo(self, message: GameMessage) -> None:
        """ツモ処理"""
        self.manager.callback(self.websocket)
        game=self.manager.get_game(self.websocket)
        if self.manager.is_callbacked(game):
            zimogiri_player=-1
            for i in range(4):
                dapai_msg = GameMessage(
                    type="game", game=GameState(action="dapai", turn=game.get_turn(i), status="thinking")
                )
                if game.players[i].socket:
                    await self.manager.send_personal_message(dapai_msg, game.players[i].socket)
                else:
                    if game.players[i].menfeng==game.teban:
                        zimogiri_player=i
                        
            
            self.manager.reset_callback(game)
            await self._handle_dapai(zimogiri=zimogiri_player)  if zimogiri_player !=-1 else None
            

    async def _handle_dapai(self, message: Optional[GameMessage]=None,zimogiri:Optional[Literal[0,1,2,3]]=None) -> None:
        """打牌処理"""
        game = self.manager.get_game(self.websocket)
        # Botのツモ切りであれば全員に通知する
        if zimogiri !=None:
            zimopai=game.players[zimogiri].shoupai.zimopai
            game.dapai(zimogiri,zimopai)
            for i in range(4):
                dapai_msg = GameMessage(
                    type="game", game=GameState(action="dapai", turn=game.get_turn(i), status="ready",dapai=zimopai.serialize())
                )
                if game.players[i].socket:
                    await self.manager.send_personal_message(dapai_msg, game.players[i].socket)
            return
        
        
        self.manager.callback(self.websocket)
        
        # プレイヤーの打牌
        if message.game.dapai:
            game.dapai(game.score.menfeng.index(game.teban), Pai.deserialize(message.game.dapai))
            for i in range(4):
                dapai_msg = GameMessage(
                    type="game", game=GameState(action="dapai", turn=game.get_turn(i), status="ready",dapai=message.game.dapai)
                )
                if game.players[i].socket and game.players[i].menfeng!=game.teban:
                    await self.manager.send_personal_message(dapai_msg, game.players[i].socket)
        
        
        if self.manager.is_callbacked(game):
            self.manager.reset_callback(game)
            game.next_teban()
            await self._send_zimo(game=game)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, manager: ConnectionManager = Depends(get_connection_manager)
):
    await manager.connect(websocket)
    handler = WebSocketMessageHandler(websocket, manager)

    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            await handler.handle_message(data)

    except WebSocketDisconnect:
        print("Client disconnected")
        manager.disconnect(websocket)

    except Exception as e:
        print(f"Error handling message: {str(e)}")
        print(f"エラー発生場所:\n{traceback.format_exc()}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
