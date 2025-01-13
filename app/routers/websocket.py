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
from app.models.type import PlayerAction,Position,PlayerStatus,Feng
from ..managers.connection import ConnectionManager
from ..models.pai import Pai
from ..models.game import Game
from ..models.shoupai import Fulou 
from ..models.websocket import (
    SimpleMessage,
    BaseMessage,
    GameMessage,
    GameState,
    ScoreContent,
    ScoreMessage,
)
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
            "kaiju": self._handle_kaiju,
            "qipai": self._handle_action,
            "zimo": self._handle_action,
            "fulou": self._handle_action,
            "dapai": self._handle_action,
            "pingju":self._handle_pingju,
        }

        handler = handlers.get(message.game.action)
        if not handler:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"不正なゲームアクション: {data}",
            )

        await handler(message)

    def _set_game_message_on_player(self,message: GameMessage):
        game=self.manager.get_game(self.websocket)
        for i in range(4):
            if game.players[i].socket==self.websocket:
                game.players[i].last_recieved_message=message
    
    async def _handle_kaiju(self, message: GameMessage) -> None:
        """開局処理"""
        new_game = self.manager.create_game(websocket=self.websocket)
        self._set_game_message_on_player(message)
        result = self.manager.callback(self.websocket)
        
        if not self.manager.is_callbacked(new_game):
            return
        
        await self._send_kaiju(new_game)
    
    async def _handle_pingju(self, message: GameMessage) -> None:
        """流局処理"""
        self._set_game_message_on_player(message)
        result = self.manager.callback(self.websocket)
        game=self.manager.get_game(self.websocket)
        if not self.manager.is_callbacked(game):
            return
        game.pingju()
        if 1<=game.score.jushu+1<=8:
            new_game = self.manager.create_game(websocket=self.websocket)
            await self._send_kaiju(new_game)
        else:
            await self._send_jieju(game)

    async def _send_zimo(self, game: Game) -> None:
        """ツモ牌送信"""
        for i in range(4):
            zimo_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="zimo",
                        turn=game.get_turn(i),
                        zimopai="b0",
                    ),
                )
            if game.players[i].menfeng==game.teban:
                zimopai=game.zimo(i)
                zimo_msg.game.fulouCandidates=game.players[i].shoupai.get_serialized_fulou_candidates()
                zimo_msg.game.lizhiPai=game.players[i].shoupai.get_serialized_lizhi_pai()
                zimo_msg.game.zimopai=zimopai.serialize()
                
            if game.players[i].socket:
                await self.manager.send_personal_message(zimo_msg, game.players[i].socket)
            game.players[i].last_sent_message=zimo_msg
    
    async def _send_jieju(self, game: Game) -> None:
        """終局送信"""
        for i in range(4):
            jieju_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="jieju",
                    ),
                )
            if game.players[i].socket:
                await self.manager.send_personal_message(jieju_msg, game.players[i].socket)
            game.players[i].last_sent_message=jieju_msg
    
    def _validate_dapai(self,last_dapai: str):
        parse_dapai=last_dapai.split(",")
        if len(parse_dapai)!=2 or not isinstance(parse_dapai[0],str) or not isinstance(int(parse_dapai[1]),int):
            raise ValueError(f"メッセージが正しくありません.[打牌,牌番号]形式にしてください. dapai:{last_dapai}")
        return parse_dapai[0],int(parse_dapai[1])
       
    async def _send_dapai(self, game: Game) -> None:
        """打牌送信"""
        lrms=[game.players[i].last_recieved_message for i in range(4)]
        last_dapai=next((x.game.dapai for x in lrms if x is not None and x.game.dapai is not None),None)
        #打牌ユーザがいない場合はボットのツモ切り
        if last_dapai is None:
            lsms=[game.players[i].last_sent_message for i in range(4)]
            last_zimo=next((x.game.zimopai for x in lsms if x is not None and x.game.zimopai is not None and x.game.zimopai!="b0"))
            
            for i in range(4):
                dapai_msg = GameMessage(
                        type="game",
                        game=GameState(
                            action="dapai",
                            turn=game.get_turn(i),
                            dapai=",".join([last_zimo,"99"])
                        ),
                    )
                if game.players[i].menfeng==game.teban:
                    game.dapai(i,Pai.deserialize(last_zimo),99)
                if game.players[i].socket:
                    await self.manager.send_personal_message(dapai_msg, game.players[i].socket)
                game.players[i].last_sent_message=dapai_msg
        else:
            dapai_str,dapai_idx=self._validate_dapai(last_dapai)
            for i in range(4):
                dapai_msg = GameMessage(
                        type="game",
                        game=GameState(
                            action="dapai",
                            turn=game.get_turn(i),
                            dapai=",".join([dapai_str,str(dapai_idx)])
                        ),
                    )
                if game.players[i].menfeng==game.teban:
                    game.dapai(i,Pai.deserialize(dapai_str),dapai_idx)
                    dapai_msg.game.fulouCandidates=game.players[i].shoupai.get_serialized_fulou_candidates()
                    dapai_msg.game.lizhiPai=game.players[i].shoupai.get_serialized_lizhi_pai()
                if game.players[i].socket:
                    await self.manager.send_personal_message(dapai_msg, game.players[i].socket)
                game.players[i].last_sent_message=dapai_msg
    
    async def _send_pingju(self, game: Game) -> None:
        """流局送信"""
        for i in range(4):
            pingju_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="pingju",
                    ),
                )
            if game.players[i].socket:
                await self.manager.send_personal_message(pingju_msg, game.players[i].socket)
            game.players[i].last_sent_message=pingju_msg
            
    async def _send_kaiju(self, game: Game) -> None:
        """開局送信"""
        for i in range(4):
            score_msg = ScoreMessage(
                score=ScoreContent(
                    baopai=[p.serialize() for p in game.score.baopai],
                    menfeng=game.score.menfeng[i],
                    paishu=70,
                    jushu=game.score.jushu,
                    zhuangfeng=game.score.zhuangfeng
                )
            )
            qipai_msg = GameMessage(type="game", game=GameState(action="qipai",qipai="+".join(
                sorted([p.serialize() for p in game.players[i].shoupai.bingpai])
            )))
            if game.players[i].socket:
                # await self._send_player_initial_state(game, i, qipai_msg)
                await self.manager.send_personal_message(
                    score_msg, game.players[i].socket
                )
                await self.manager.send_personal_message(
                    qipai_msg, game.players[i].socket
                )
            game.players[i].last_sent_message=qipai_msg
    
    async def _send_fulou(self, game: Game) -> None:
        """副露送信"""
        fulou_str=game.get_last_recieved_fulou()
        for i in range(4):
            fulou_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="fulou",
                        turn=game.get_turn(i),
                        fulou=fulou_str
                    ),
                )
            
            if game.players[i].menfeng==game.teban:
                game.fulou(i,Fulou.deserialize(fulou_str))
                
            if game.players[i].socket:
                await self.manager.send_personal_message(fulou_msg, game.players[i].socket)
            game.players[i].last_sent_message=fulou_msg
    
    async def _handle_action(self, message: GameMessage) -> None:
        """メッセージ処理"""
        self.manager.callback(self.websocket)
        self._set_game_message_on_player(message)
        game=self.manager.get_game(self.websocket)
        
        if not self.manager.is_callbacked(game):
            return
        
        lsms=[game.players[i].last_sent_message for i in range(4)]
        last_action=next((x.game.action for x in lsms if x is not None and x.game.action is not None))
        # recieved_action:List[Union[PlayerAction,None]]=[game.players[i].last_recieved_message.game.action if game.players[i].last_recieved_message else None  for i in range(4) ]
        # print("last_action,recieved_action",last_action,recieved_action)
        if last_action=="qipai":
            await self._send_zimo(game=game)
            self.manager.reset_callback(game)
        elif last_action=="zimo":
            await self._send_dapai(game=game)
            self.manager.reset_callback(game)
        elif last_action=="dapai":
            if any(p.last_recieved_message and p.last_recieved_message.game.fulou for p in game.players):
                idx=game.get_last_recieved_fulou_player()
                game.teban=game.players[idx].menfeng
                print("idx",idx)
                await self._send_fulou(game=game)
            else:
                if len(game.shan.pais)==0:
                    await self._send_pingju(game=game)
                else:
                    game.next_teban()
                    await self._send_zimo(game=game)
            self.manager.reset_callback(game)
        elif last_action=="fulou":
            await self._send_dapai(game=game)
            self.manager.reset_callback(game)
            
            


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
