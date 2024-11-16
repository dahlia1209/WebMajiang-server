from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional, Self
from .player import Player
from .pai import Pai
from .shan import Shan
from .wangpai import Wangpai
from .shoupai import Shoupai
from .he import He
from .score import Score
from .rule import Rule
from .type import Feng, PlayerAction, Position
import random


class Game(BaseModel):
    players: List[Player] = Field(default=[])
    shan: Shan = Field(default=Shan())
    wangpai: Wangpai = Field(default=Wangpai())
    rule: Rule = Field(default=Rule())
    score: Score = Field(default=Score())
    teban: Feng = Field(default="東")

    def qipai(self, other: Optional[Self] = None):
        if other:
            self.players = other.players
            self.score = other.score
            self.rule = other.rule
        # 数牌（赤ドラ以外）生成
        normal_pais = [
            Pai(suit=suit, num=num)
            for suit in ["m", "p", "s"]
            for num in range(1, 10)
            for _ in range(4 if num != 5 else 3)
        ]

        # 赤ドラ生成
        red_pais = [Pai(suit=suit, num=5, is_red=True) for suit in ["m", "p", "s"]]

        # 字牌生成
        honor_pais = [Pai(suit="z", num=num) for num in range(1, 8) for _ in range(4)]

        # 全牌セット
        all_pais = normal_pais + red_pais + honor_pais
        random.shuffle(all_pais)

        # 王牌セット
        wangpai = [all_pais.pop() for _ in range(14)]
        self.wangpai = Wangpai(
            lingshangpai=wangpai[:4], baopai=wangpai[4:9], libaopai=wangpai[9:14]
        )
        # 通知用メッセージにドラ設定
        self.score = Score(baopai=self.wangpai.get_baopai())

        # 手牌セット
        for i in range(4):
            bingpai = [all_pais.pop() for _ in range(13)]
            self.players[i].shoupai = Shoupai(bingpai=bingpai)
            self.players[i].he = He()

        # 山牌セット
        self.shan = Shan(pais=all_pais)

        # 自風決め
        if other:
            t = self.players[0].menfeng
            self.players[0].menfeng = self.players[1].menfeng
            self.players[1].menfeng = self.players[2].menfeng
            self.players[2].menfeng = self.players[3].menfeng
            self.players[3].menfeng = t
            for i in range(4):
                self.players[i].menfeng
            self.score.menfeng=[self.players[i].menfeng for i in range(4)]
                
        else:
            random.shuffle(self.players)
            for i, f in enumerate(["東", "南", "西", "北"]):
                self.players[i].menfeng = f
                self.score.menfeng[i] = f

    def zimo(self, num: Literal[0, 1, 2, 3]):
        """
        Args:
            num (Literal[0, 1, 2, 3]):
                - 0: 起家
                - 1: 下家
                - 2: 対面
                - 3: 上家
        """
        zimopai = self.shan.pop()
        self.players[num].shoupai.set_zimopai(zimopai)
        return zimopai

    def dapai(self, num: Literal[0, 1, 2, 3], dapai: Pai):
        self.players[num].shoupai.remove_pai(dapai)

    def bot_action(self, action: PlayerAction):
        pass

    def get_turn(self, num: Literal[0, 1, 2, 3]) -> Position:
        if self.players[num].menfeng == self.teban:
            return "main"

        position_map = {
            "東": {"南": "xiajia", "西": "duimian", "北": "shangjia"},
            "南": {"東": "shangjia", "西": "xiajia", "北": "duimian"},
            "西": {"東": "duimian", "南": "shangjia", "北": "xiajia"},
            "北": {"東": "xiajia", "南": "duimian", "西": "shangjia"},
        }

        return position_map[self.players[num].menfeng][self.teban]

    def next_teban(self):
        if self.teban == "東":
            self.teban = "南"
        elif self.teban == "南":
            self.teban = "西"
        elif self.teban == "西":
            self.teban = "北"
        else:
            self.teban = "東"
        return self.teban
