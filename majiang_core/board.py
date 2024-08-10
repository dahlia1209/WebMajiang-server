from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union,Literal
from .rule import RuleConfig
from .shan import Shan
from enum import Enum
from .shoupai import Shoupai
from .he import He

class Kaiju(BaseModel):
    id: Optional[int] = Field(default=0)
    title: str
    player: List[str]
    qijia: int
    zhuangfeng: Optional[int] = Field(default=None)
    jushu: Optional[int] = Field(default=None)
    changbang: Optional[int] = Field(default=None)
    lizhibang: Optional[int] = Field(default=None)
    defen: Optional[List[int]] = Field(default=None)
    shan: Optional[Any] = Field(default=None)
    rule: Optional[Any] = Field(default=None)
    shoupai: Optional[List[Shoupai]] = Field(default=None)
    he: Optional[List[Any]] = Field(default=None)
    player_id: Optional[List[int]] = Field(default=None)
    lunban: Optional[Any] = None
    
    
# class NakiType(str, Enum):
#     chi = 'chi'
#     peng = 'peng'
#     gang = 'gang'
#     lizhi = 'lizhi'
#     rong = 'rong'
#     zimo = 'zimo'
    
class Board(BaseModel):
    title: Optional[str] = None
    player: Optional[List[str]] = None
    qijia: Optional[int] = None
    zhuangfeng: Optional[int] = None
    jushu: Optional[int] = None
    changbang: Optional[int] = None
    lizhibang: Optional[int] = None
    defen: Optional[List[int]] = None
    shan: Optional[Shan] = None
    shoupai: Optional[List[Shoupai]] = None
    he: Optional[List[He]] = None
    player_id: Optional[List[int]] = None
    lunban: int = -1
    lizhi: Optional[Any] = Field(default=None, alias="_lizhi")
    fenpei: Optional[Any] = Field(default=None, alias="_fenpei")

    def set_audio(self, audio: Any):
        pass

    def redraw(self):
        pass

    def update(self, data: Any = {}):
        pass

    def say(self, name: Literal["HELLO", "ROOM", "START", "END", "ERROR", "disconnect","GAME"], l: Any):
        pass

    def summary(self, paipu: Any):
        pass

    def players(self, players: Any):
        pass

    def kaiju(self, kaiju: Kaiju):
        self.title = kaiju.title
        self.player = kaiju.player
        self.qijia = kaiju.qijia
        self.zhuangfeng = kaiju.zhuangfeng or 0
        self.jushu = kaiju.jushu or 0
        self.changbang = kaiju.changbang or 0
        self.lizhibang = kaiju.lizhibang or 0
        self.defen = kaiju.defen or []
        self.shan = kaiju.shan or None
        self.shoupai = kaiju.shoupai or [None]*4
        self.he = kaiju.he or [None]*4
        self.player_id = kaiju.player_id or [0, 1, 2, 3]
        self.lunban = kaiju.zhuangfeng if kaiju.zhuangfeng is not None else -1
        self.lizhi = None
        self.fenpei = None
    
    def update_shoupai(self, data: List[dict]):
        new_shoupai = [Shoupai(**shoupai) for shoupai in data]
        self.shoupai = new_shoupai
        
    def update_he(self, data: List[dict]):
        new_he = [He(**he) for he in data]
        self.he = new_he
    
    def update_shan(self, data: dict):
        new_shan = Shan(self.shan.rule,**data)
        self.shan = new_shan

