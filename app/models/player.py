from pydantic import BaseModel, Field, PrivateAttr,ConfigDict
from typing import List, Dict, Tuple, Literal, Optional
from .shoupai import Shoupai
from .type import Feng
from .user import User
from .he import He
from .websocket import GameMessage
from fastapi import WebSocket


class Player(BaseModel):
    shoupai: Shoupai = Field(default_factory=Shoupai)
    menfeng: Feng = Field(default=None)
    user: Optional[User] = Field(default=None)
    he: He = Field(default_factory=He)
    socket: Optional[WebSocket]=Field(default=None)
    last_recieved_message:Optional[GameMessage]=Field(default=None)
    last_sent_message:Optional[GameMessage]=Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def is_recieved_message(self):
        return self.last_recieved_message is not None and (
            self.last_recieved_message.game.action == "kaiju"
            or (
                self.last_sent_message is not None
                and self.last_recieved_message.game.action
                == self.last_sent_message.game.action
            )
        )
        
    def is_bot(self):
        return self.socket is None
