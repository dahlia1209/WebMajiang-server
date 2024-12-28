from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from app.models.player import Player
from app.models.shan import Shan
from app.models.he import He
from app.models.pai import Pai
from app.models.shoupai import Fulou, FulouType
from app.models.wangpai import Wangpai


class PlayerService(BaseModel):
    player: Player = Field(default=Player())

    def zimo(self, shan: Shan):
        pai = shan.pop()
        self.player.shoupai.do_zimo(pai)

    def dapai(self, pai: Pai, is_zimopai: bool = False):
        self.player.he.add_pai(pai)
        if is_zimopai and pai == self.player.shoupai.zimopai:
            self.player.shoupai.remove_pai_from_zimopai()
        elif pai in self.player.shoupai.bingpai:
            self.player.shoupai.remove_pai_from_bingpai(pai)
        else:
            raise ValueError(f"指定された牌は手牌にありません:{pai}")

    def fulou(self, fulou: Fulou, he: He = None, wangpai: Wangpai = None):
        if fulou.type in ["angang","jiagang"] and wangpai:
            self.player.shoupai.do_fulou(fulou=fulou)
            lingshangpai = wangpai.pop_lingshangpai()
            self.player.shoupai.do_zimo(lingshangpai)
        elif fulou.type == "minggang" and wangpai and he:
            nakipai = he.pop()
            if nakipai.num == fulou.nakipai.num and nakipai.suit == fulou.nakipai.suit: 
                self.player.shoupai.do_fulou(fulou=fulou)
                lingshangpai = wangpai.pop_lingshangpai()
                self.player.shoupai.do_zimo(lingshangpai)
            else:
                raise ValueError(f"指定された鳴牌では副露できません.fulou:{fulou},nakipai:{nakipai}")
        elif fulou.type in ["chi","peng"]  and he:
            nakipai = he.pop()
            if nakipai.num == fulou.nakipai.num and nakipai.suit == fulou.nakipai.suit: 
                self.player.shoupai.do_fulou(fulou=fulou)
            else:
                raise ValueError(f"指定された鳴牌では副露できません.fulou:{fulou},nakipai:{nakipai}")
        else:
            raise ValueError(f"指定された副露ができません。捨て牌:{lingshangpai},fulou{fulou}")
    
    def hule(self,hule_pai: Pai):
        for pai in self.player.shoupai.hule_candidates:
            if hule_pai.num==pai.num and hule_pai.suit==pai.suit:
                pass
             
