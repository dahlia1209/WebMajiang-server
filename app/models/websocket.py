from pydantic import BaseModel, Field, PrivateAttr, field_validator,ConfigDict
from fastapi import APIRouter, WebSocket
from uuid import UUID,uuid4
from typing import Literal,Optional,Union,List,Any
from .type import PlayerAction,Position,PlayerStatus,Feng
class WebSocketModel(BaseModel):
    uid:UUID=uuid4()
    websocket: WebSocket
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
MessageType = Literal["message","game"]

# ベースメッセージモデル
class BaseMessage(BaseModel):
    type: MessageType

# ゲームの状態を表すモデル
class GameState(BaseModel):
    action: Optional[PlayerAction] = None
    turn: Optional[Position] = None
    status: Optional[PlayerStatus] = None
    dapai: Optional[str] = None
    zimopai: Optional[str] = None
    canFulouList: Optional[List[str]] = None
    fulou: Optional[str] = None
    qipai: Optional[str] = None
    
class ScoreContent(BaseModel):
    zhuangfeng: Optional[Feng] = None
    menfeng: Optional[Feng] = None
    jushu: Optional[int] = None
    jicun: Optional[int] = None
    changbang: Optional[int] = None
    defen: Optional[List[int]] = None
    baopai: Optional[List[str]] = None

# ゲームメッセージモデル
class GameMessage(BaseMessage):
    type: MessageType="game"
    game: GameState
    
class ScoreMessage(BaseMessage):
    type: MessageType="score"
    score: ScoreContent
    

class SimpleMessage(BaseMessage):
    type: MessageType="message"
    msg: Any


# すべてのメッセージタイプの Union
WebSocketMessage = Union[SimpleMessage,GameMessage,ScoreMessage]