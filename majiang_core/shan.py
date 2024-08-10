from .rule import RuleConfig
from pydantic import BaseModel, Field,AliasChoices
from typing import List, Optional
import random
from .shoupai import Shoupai


class Shan(BaseModel):
    rule: RuleConfig = Field(default=None,alias="_rule")
    pai: List[str] = Field(default=[],alias="_pai")
    baopai: List[str] = Field(default=[],alias="_baopai")
    fubaopai: List[str] = Field(default=[], alias= "_fubaopai")
    weikaigang: bool = Field(default=False,alias="_weikaigang")
    closed: bool = Field(default=False,alias="_closed")

    @staticmethod
    def zhenbaopai(p: str) -> str:
        if not Shan.valid_pai(p):
            raise ValueError(p)
        s, n = p[0], int(p[1]) if len(p) > 1 else 5
        return s + (
            str((n % 9) + 1)
            if s != "z"
            else str((n % 4) + 1) if n < 5 else str(((n - 4) % 3) + 5)
        )

    @staticmethod
    def valid_pai(p: str) -> bool:
        # 牌の検証ロジックが必要です。ここではプレースホルダーとして True を返します。
        return True

    def __init__(self, rule: RuleConfig,**data):
        super().__init__(**data)
        self.rule = rule
        hongpai = rule.赤牌
        pai = []
        suits = ["m", "p", "s", "z"]
        for s in suits:
            for n in range(1, 8 if s == "z" else 10):
                for i in range(4):
                    if n == 5 and i < hongpai.get(s, 0):
                        pai.append(f"{s}0")
                    else:
                        pai.append(f"{s}{n}")

        random.shuffle(pai)
        self.pai = pai
        self.baopai = [self.pai[4]]
        self.fubaopai = [self.pai[9]] if rule.裏ドラあり else None
        # self.weikaigang = False
        # self.closed = False

    @property
    def paishu(self):
        return len(self.pai) - 14

    def zimo(self):
        if self.closed:
            raise ValueError(f"Shan object is closed: {self.__dict__}")
        if self.paishu == 0:
            raise ValueError(f"No tiles left: {self.__dict__}")
        if self.weikaigang:
            raise ValueError(f"Weikaigang error: {self.__dict__}")
        return self.pai.pop()
    
    def close(self):
        self.closed = True
        return self
    

    def kaigang(self) -> 'Shan':
        if self.closed:
            raise ValueError(self.model_dump_json())
        if not self.weikaigang:
            raise ValueError(self.model_dump_json())
        
        self.baopai.append(self.pai[4])
        if self.fubaopai is not None and self.rule.カン裏あり:
            self.fubaopai.append(self.pai[9])
        
        self.weikaigang = False
        return self