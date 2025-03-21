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
from ..models.player import Player
from ..models.shoupai import Fulou 
from ..models.rule import Rule 
from ..models.websocket import (
    SimpleMessage,
    BaseMessage,
    GameMessage,
    GameState,
    ScoreContent,
    ScoreMessage,
)
import traceback
from itertools import chain
from threading import local,Lock

router = APIRouter()

class WebSocketMessageHandler:
    _instance = None
    _initialized = False
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, connection_manager=None):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.manager = connection_manager or ConnectionManager()
                    # スレッドローカルではなく、WebSocketをキーとした辞書を使用
                    self.websocket_map = {}
                    self.games:List[Game] = []
                    self._initialized = True
    
    def _set_local_websocket(self,websocket:WebSocket):
        socket_id = str(id(websocket))
        self.websocket_map[socket_id] = websocket
        return socket_id

    def _get_local_websocket(self) :
        websocket:WebSocket= getattr(self._thread_local, 'websocket', None)
        if websocket is None:
            raise ValueError("Websokcetがセットされていません")
        return websocket
    
    def _get_game(self, websocket: WebSocket):
        for game in self.games:
            for player in game.players:
                if player.socket and id(player.socket) == id(websocket):
                    return game
        return None
    
    def _remove_game(self, websocket: WebSocket):
        game = self._get_game(websocket)
        if game is None:
            return
        
        self.games.remove(game)
        return game
    
    def _create_game(self, websocket: WebSocket, rule: Rule = Rule()):
        # すでに存在するゲームを確認
        current_game = self._get_game(websocket)
        if current_game:
            # 新しいゲームを作成し、現在のゲームをアップデート
            new_game = current_game.next_game()
            self._remove_game(websocket)
        else:
            # 新しいゲームを作成
            new_game = Game(rule=rule, players=[Player(socket=websocket)] + [Player() for _ in range(3)])
            new_game.select_zuoci()
            
        new_game.qipai()
        self.games.append(new_game)
        return new_game

    async def handle_message(self, message_data: dict, websocket: WebSocket) -> None:
        """メインのメッセージハンドリングフロー"""
        try:
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

            await handler(message_data, websocket)
        except Exception as e:
            print(f"メッセージ処理中にエラーが発生しました: {str(e)}")
            print(f"エラー発生場所:\n{traceback.format_exc()}")
            raise

    async def _handle_simple_message(self, data: dict, websocket: WebSocket) -> None:
        """シンプルメッセージの処理"""
        message = SimpleMessage(**data)
        await websocket.send_json(message.model_dump())

    async def _handle_game_message(self, data: dict, websocket: WebSocket) -> None:
        """ゲームメッセージの処理"""
        message = GameMessage(**data)
        handlers = {
            "kaiju": self._handle_kaiju,
            "qipai": self._handle_qipai,
            "zimo": self._handle_zimo,
            "fulou": self._handle_fulou,
            "dapai": self._handle_dapai,
            "pingju": self._handle_pingju,
            "hule": self._handle_hule,
            "lizhi": self._handle_lizhi,
        }

        handler = handlers.get(message.game.action)
        if not handler:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"不正なゲームアクション: {data}",
            )

        await handler(message, websocket)

    def _handle_callback(self,message: GameMessage, websocket: WebSocket):
        """受信したメッセージをプレイヤーに関連付ける"""
        game = self._get_game(websocket)
        if game is None:
            raise ValueError("Gameが存在しないためコールバック処理ができません。")
        
        # 現在のWebSocketに対応するプレイヤーを見つける
        for player in game.players:
            if player.socket and id(player.socket) == id(websocket):
                player.last_recieved_message = message
                break
        
    
    def _is_callbacked(self, game: Game):
        """全てのプレイヤーがメッセージを受信したかチェック"""
        if game is None:
            raise ValueError("Gameが存在しないためコールバック処理ができません。")
        
        return all(
            game.players[i].is_recieved_message()
            for i in range(4) if not game.players[i].is_bot()
        )
        
    

    async def _send_zimo(self, game: Game,zimopai:Pai,baopai:Optional[Pai]=None) -> None:
        """ツモ牌送信"""
        for i in range(4):
            fulouCandidates=None
            lizhipai=None
            hule=None
            zimopai_str="b0"
            baopai_str=None if not baopai else baopai.serialize()
            if game.get_zuoci_player()[0]==i:
                fulouCandidates=game.players[i].shoupai.get_serialized_fulou_candidates()
                lizhipai=game.players[i].shoupai.get_serialized_lizhi_pai()
                hule=game.get_serialized_hule_pai(i)
                zimopai_str=zimopai.serialize()
                
            zimo_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="zimo",
                        turn=game.get_turn(i),
                        zimopai=zimopai_str,
                        fulouCandidates=fulouCandidates,
                        lizhipai=lizhipai,
                        hule=hule,
                        baopai=baopai_str,
                    ),
                )
                
            if not game.players[i].is_bot():
                await self.manager.send_personal_message(zimo_msg, game.players[i].socket)
            game.players[i].last_sent_message=zimo_msg
    
    async def _send_lingshangzimo(self, game: Game,zimopai:Pai,baopai:Pai) :
        await self._send_zimo(game,zimopai,baopai)
    
    async def _send_jieju(self, game: Game) -> None:
        """終局送信"""
        for i in range(4):
            jieju_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="jieju",
                    ),
                )
            if not game.players[i].is_bot():
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
                            dapai=",".join([last_zimo,"99"]),
                        ),
                    )
                if game.get_zuoci_player()[0]==i:
                    game.dapai(i,Pai.deserialize(last_zimo),99)
                if not game.players[i].is_bot():
                    dapai_msg.game.hule=game.get_serialized_hule_pai(i,True)
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
                if game.get_zuoci_player()[0]==i:
                    game.dapai(i,Pai.deserialize(dapai_str),dapai_idx)
                    dapai_msg.game.fulouCandidates=game.players[i].shoupai.get_serialized_fulou_candidates()
                    dapai_msg.game.lizhipai=game.players[i].shoupai.get_serialized_lizhi_pai()
                    dapai_msg.game.hule=game.get_serialized_hule_pai(i,True)
                if not game.players[i].is_bot():
                    await self.manager.send_personal_message(dapai_msg, game.players[i].socket)
                game.players[i].last_sent_message=dapai_msg
    
    async def _send_lizhi(self, game: Game) -> None:
        """立直送信"""
        lrms=[game.players[i].last_recieved_message for i in range(4)]
        last_dapai=next((x.game.dapai for x in lrms if x is not None and x.game.dapai is not None),None)
        lizhipai_str,lizhipai_idx=self._validate_dapai(last_dapai)
        for i in range(4):
            lizhipai_msg = GameMessage(
                type="game",
                game=GameState(
                    action="lizhi",
                    turn=game.get_turn(i),
                    dapai=",".join([lizhipai_str,str(lizhipai_idx)])
                ),
            )
            if not game.players[i].is_bot():
                await self.manager.send_personal_message(lizhipai_msg, game.players[i].socket)
            game.players[i].last_sent_message=lizhipai_msg
    
    async def _send_pingju(self, game: Game) -> None:
        """流局送信"""
        for i in range(4):
            pingju_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="pingju",
                    ),
                )
            if not game.players[i].is_bot():
                await self.manager.send_personal_message(pingju_msg, game.players[i].socket)
            game.players[i].last_sent_message=pingju_msg
            
    async def _send_hule(self, game: Game) -> None:
        """和了送信"""
        for i in range(4):
            hule_msg = GameMessage(
                    type="game",
                    game=GameState(
                        action="hule",
                        turn=game.get_turn(i),
                        
                    ),
                )
            if not game.players[i].is_bot():
                await self.manager.send_personal_message(hule_msg, game.players[i].socket)
            game.players[i].last_sent_message=hule_msg
            
    async def _send_kaiju(self, game: Game) -> None:
        """開局送信"""
        for i in range(4):
            score_msg = ScoreMessage(
                score=ScoreContent(
                    baopai=[p.serialize() for p in game.score.baopai],
                    menfeng=game.score.menfeng[i],
                    paishu=70,
                    jushu=game.score.jushu,
                    zhuangfeng=game.score.zhuangfeng,
                    defen=game.score.defen,
                )
            )
            qipai_msg = GameMessage(type="game", game=GameState(
                action="qipai",qipai="+".join(sorted([p.serialize() for p in game.players[i].shoupai.bingpai])),
                fulouCandidates=game.players[i].shoupai.get_serialized_fulou_candidates()
                ),
                                    )
            if not game.players[i].is_bot():
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
                
            if not game.players[i].is_bot():
                await self.manager.send_personal_message(fulou_msg, game.players[i].socket)
            game.players[i].last_sent_message=fulou_msg
    
    
    async def _handle_kaiju(self, message: GameMessage, websocket: WebSocket) -> None:
        """開局処理"""
        #処理サブ関数
        async def process_kaiju():
           await self._send_kaiju(new_game)
        
        #メイン処理
        new_game = self._create_game(websocket)
        self._handle_callback(message, websocket)
        
        if not self._is_callbacked(new_game):
            return
        
        next_action,player=self._get_next_action(new_game)
        processes = {
            "kaiju": process_kaiju,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
    
    async def _handle_pingju(self, message: GameMessage, websocket: WebSocket) -> None:
        """流局処理"""
        #処理サブ関数
        async def process_pingju():
            game.pingju()
            if 1<=game.score.jushu+1<=8:
                new_game = self._create_game(websocket)
                await self._send_kaiju(new_game)
            else:
                await self._send_jieju(game) 
        
        #メイン処理
        self._handle_callback(message,websocket)
        game=self._get_game(websocket)
        
        if not self._is_callbacked(game):
            return
        
        next_action,player=self._get_next_action(game)
        processes = {
            "pingju": process_pingju,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
               
    
    async def _handle_qipai(self, message: GameMessage, websocket: WebSocket) -> None:
        """配牌処理"""
        #処理サブ関数
        async def process_qipai():
            zimopai=game.zimo(game.get_zuoci_player()[0])
            await self._send_zimo(game,zimopai)
        
        #メイン処理
        self._handle_callback(message,websocket)
        game=self._get_game(websocket)
        
        if not self._is_callbacked(game):
            return
        
        next_action,player=self._get_next_action(game)
        processes = {
            "qipai": process_qipai,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
            
    async def _handle_dapai(self, message: GameMessage, websocket: WebSocket) -> None:
        """打牌後のリアクションのハンドリング"""
        #処理サブ関数
        async def process_hule():
            if game.players[player].last_recieved_message is None or  game.players[player].last_recieved_message.game.hule is None:
                raise ValueError("和了牌が存在しません")
            hulepai=Pai.deserialize(game.players[player].last_recieved_message.game.hule)
            hupai=game.hule(player,hulepai)
            game.zuoci=game.players[player].menfeng
            await self._send_hule(game=game)
        async def process_fulou():
            game.zuoci=game.players[player].menfeng
            game.fulou(player,Fulou.deserialize(game.get_last_recieved_fulou()))
            await self._send_fulou(game=game)
        async def process_dapai():
            if len(game.shan.pais)==0:
                await self._send_pingju(game=game)
            else:
                game.next_zuoci()
                zimopai=game.zimo(game.get_zuoci_player()[0])
                await self._send_zimo(game,zimopai)
        
        #メイン処理
        self._handle_callback(message,websocket)
        game=self._get_game(websocket)
        
        if not self._is_callbacked(game):
            return
        next_action,player=self._get_next_action(game)
        processes = {
            "hule": process_hule,
            "fulou": process_fulou,
            "dapai": process_dapai,
            "lizhi": process_dapai,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
    
    async def _handle_lizhi(self, message: GameMessage, websocket: WebSocket) -> None:
        """立直宣言後のリアクションのハンドリング"""
        await self._handle_dapai(message,websocket)
        
    
    async def _handle_zimo(self, message: GameMessage, websocket: WebSocket) -> None:
        """自摸後のリアクションのハンドリング"""
        #処理サブ関数
        async def process_hule():
            if game.players[player].last_recieved_message is None or  game.players[player].last_recieved_message.game.hule is None:
                raise ValueError("和了牌が存在しません")
            hulepai=Pai.deserialize(game.players[player].last_recieved_message.game.hule)
            game.hule(player,hulepai)
            await self._send_hule(game=game)
        async def process_lizhi():
            if   game.players[player].last_recieved_message is None or  game.players[player].last_recieved_message.game.lizhipai is None:
                raise ValueError("和了牌が存在しません")
            dapai_str,dapai_idx=self._validate_dapai(game.players[player].last_recieved_message.game.dapai)
            game.lizhi(player,Pai.deserialize(dapai_str),dapai_idx)
            await self._send_lizhi(game=game)
        async def process_fulou():
            game.fulou(player,Fulou.deserialize(game.get_last_recieved_fulou()))
            await self._send_fulou(game=game)
        async def process_dapai():
            await self._send_dapai(game=game)
        async def process_zimo():
            await self._send_dapai(game=game)
        
        #メイン処理
        self._handle_callback(message,websocket)
        game=self._get_game(websocket)
        
        if not self._is_callbacked(game):
            return
        next_action,player=self._get_next_action(game)
        processes = {
            "hule": process_hule,
            "fulou": process_fulou,
            "dapai": process_dapai,
            "lizhi": process_lizhi,
            "zimo": process_zimo,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
    
    async def _handle_fulou(self, message: GameMessage, websocket: WebSocket) -> None:
        """副露処理"""
        #処理サブ関数
        async def process_hule():
            pass
        async def process_fulou():
            game.fulou(player,Fulou.deserialize(game.get_last_recieved_fulou()))
            await self._send_fulou(game=game)
        async def process_dapai():
            await self._send_dapai(game=game)
        async def process_zimo():
            zimopai,gangbaopai=game.lingshangzimo(game.get_zuoci_player()[0])
            await self._send_lingshangzimo(game,zimopai,gangbaopai)
        
        #メイン処理
        self._handle_callback(message,websocket)
        game=self._get_game(websocket)
        
        if not self._is_callbacked(game):
            return
        next_action,player=self._get_next_action(game)
        processes = {
            "hule": process_hule,
            "fulou": process_fulou,
            "dapai": process_dapai,
            "zimo": process_zimo,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
        
    async def _handle_hule(self, message: GameMessage, websocket: WebSocket) -> None:
        """和了処理"""
        #処理サブ関数
        async def process_hule():
            if 1<=game.score.jushu+1<=8:
                new_game = self._create_game(websocket)
                await self._send_kaiju(new_game)
            else:
                await self._send_jieju(game)
        
        #メイン処理
        self._handle_callback(message,websocket)
        game=self._get_game(websocket)
        
        if not self._is_callbacked(game):
            return
        next_action,player=self._get_next_action(game)
        processes = {
            "hule": process_hule,
        }
        process=processes.get(next_action)
        if not process:
            raise ValueError(f"次のアクションが不正です,next_action:{next_action}")
        await process()
        
    def _get_next_action(self,game:Game):
        next_action:Union[PlayerAction,None]
        player:int
        
        player,next_action=next(
            chain(
                ((i,"hule") for i,p in enumerate(game.players) if p.last_recieved_message and p.last_recieved_message.game.hule),
                ((i,"lizhi") for i,p in enumerate(game.players) if p.last_recieved_message and p.last_recieved_message.game.lizhipai),
                ((i,"fulou") for i,p in enumerate(game.players) if p.last_recieved_message and p.last_recieved_message.game.fulou),
                ((i,"dapai") for i,p in enumerate(game.players) if p.last_recieved_message and p.last_recieved_message.game.dapai),
                ((i,"zimo") for i,p in enumerate(game.players) if p.last_recieved_message and p.last_recieved_message.game.zimopai),
                ((i,p.last_recieved_message.game.action) for i,p in enumerate(game.players) if p.last_recieved_message and p.last_recieved_message.game.action is not None)
                ),
            (-1,None))
        
        if next_action is None:
            raise ValueError("次のアクションが取得できません")
        
        return next_action,player

def get_websocket_handler_manager():
    return WebSocketMessageHandler()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, handler: WebSocketMessageHandler = Depends(get_websocket_handler_manager)
):
    await handler.manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received message: {data}")
            await handler.handle_message(data,websocket)
    
    except WebSocketDisconnect:
        print("Client disconnected")
        handler.manager.disconnect(websocket)

    except Exception as e:
        print(f"Error handling message: {str(e)}")
        print(f"エラー発生場所:\n{traceback.format_exc()}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

