from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from .shoupai import Shoupai
from .type import Feng
from .user import User
from .he import He

class Player(BaseModel):
    shoupai:Shoupai= Field(default=Shoupai())
    menfeng:Feng=Field(default=None)
    user:User=Field(default=User.guest())
    he:He=Field(default=He())
    is_lizhi:bool=Field(default=False)
    
