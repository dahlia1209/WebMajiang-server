from pydantic import BaseModel, Field, PrivateAttr, field_validator,ConfigDict
from fastapi import APIRouter, WebSocket
from uuid import UUID,uuid4
from typing import Literal,Optional,Union,List,Any
from .type import PlayerAction,Position,PlayerStatus,Feng
class WebSocketModel(BaseModel):
    uid:UUID=uuid4()
    websocket: WebSocket
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
MessageType = Literal["message","game","score"]


# ゲームの状態を表すモデル
class GameState(BaseModel):
    action: Optional[PlayerAction] = Field(default=None)
    turn: Optional[Position] = Field(default=None)
    # status: Optional[PlayerStatus] = Field(default=None)
    dapai: Optional[str] = Field(default=None)
    zimopai: Optional[str] = Field(default=None)
    fulouCandidates: Optional[str] = Field(default=None)
    lizhiPai: Optional[str] = Field(default=None)
    fulou: Optional[str] = Field(default=None)
    qipai: Optional[str] = Field(default=None)
    
class ScoreContent(BaseModel):
    zhuangfeng: Optional[Feng] = Field(default="東")
    menfeng: Optional[Feng] = Field(default="東")
    jushu: Optional[int] = Field(default=1)
    jicun: Optional[int] = Field(default=0)
    changbang: Optional[int] = Field(default=0)
    defen: Optional[List[int]] = Field(default=[25000,25000,25000,25000])
    baopai: Optional[List[str]] = Field(default=["b0","b0","b0","b0","b0"])
    paishu:Optional[int]=Field(default=70)

# ベースメッセージモデル
class BaseMessage(BaseModel):
    type: MessageType
    # msg:Union[GameState,ScoreContent]


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