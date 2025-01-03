from pydantic import BaseModel, Field, PrivateAttr,ConfigDict
from typing import List, Dict, Tuple, Literal, Optional
from .shoupai import Shoupai
from .type import Feng
from .user import User
from .he import He
from .websocket import GameMessage
from fastapi import WebSocket


class Player(BaseModel):
    shoupai: Shoupai = Field(default=Shoupai())
    menfeng: Feng = Field(default=None)
    user: Optional[User] = Field(default=None)
    he: He = Field(default=He())
    # is_lizhi: bool = Field(default=False)
    # is_yifa:bool=Field(default=False)
    socket: Optional[WebSocket]=Field(default=None)
    last_recieved_message:Optional[GameMessage]=Field(default=None)
    last_sent_message:Optional[GameMessage]=Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)