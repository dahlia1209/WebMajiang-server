from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from .player import Player
from .shan import Shan
from .rule import Rule
from .type import Feng

class Game(BaseModel):
    players:List[Player]=Field(default=[])
    shan:Shan=Field(default=Shan())
    rule:Rule=Field(default=Rule())
    zhuangfeng:Feng=Field(default=None)
    honba:int=Field(default=1)
    