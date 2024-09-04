from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from app.models.shan import Shan
from app.models.he import He
from app.models.rule import Rule
from app.models.pai import Pai
from app.models.type import PaiSuit
from app.models.game import Game
from .player_service import PlayerService
import random

class GameService(BaseModel):
    game:Game=Field(default=Game())
    player_service:PlayerService=Field(default=PlayerService())
    def qipai(self):
        #136枚の牌を生成
        def generate_all_pais():
            all_pais:List[Pai]=[]
            for suit in ['m','p','s']:
                for num in range(1, 10):
                    for _ in range(0,4):
                        all_pais.append(Pai(num=num,suit=suit))
            for num in range(1,8):
                for _ in range(0,4):
                    all_pais.append(Pai(num=num,suit='z'))
                
            return all_pais
        all_pais=generate_all_pais()
        #赤ドラセット
        for p in self.game.rule.red_pais:
             all_pais.remove(Pai(num=p.num,suit=p.suit))
             all_pais.append(p)
        #牌をシャッフル
        random.shuffle(all_pais)
        
        #牌をセット
        self.game.shan.pais=all_pais[:70]
        