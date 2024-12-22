from pydantic import BaseModel, field_validator, ConfigDict,Field
from typing import Literal,Dict,ClassVar
from .type import PaiSuit

class Pai(BaseModel):
    suit: PaiSuit
    num: int
    is_red: bool = False
    model_config = ConfigDict(frozen=True)

    @field_validator('num')
    @classmethod
    def validate_num(cls, v, values):
        suit = values.data.get('suit')
        if suit in ['m', 'p', 's']:
            if v not in range(1, 10):
                raise ValueError('Number must be between 1 and 9 for suits m, p, s')
        elif suit == 'z':
            if v not in range(1, 8):
                raise ValueError('Number must be between 1 and 7 for suit z')
        return v


    @field_validator('is_red')
    @classmethod
    def validate_is_red(cls, v, values):
        suit = values.data.get('suit')
        num = values.data.get('num')
        if v and (suit == 'z' or num != 5):
            raise ValueError('Only 5 in suits m, p, s can be red dora')
        return v
    
    def __eq__(self, other):
        if isinstance(other, Pai):
            return self.num == other.num and self.suit == other.suit and self.is_red == other.is_red 
        return False
    
    def serialize(self):
        return str(self.suit)+str(self.num)+('t' if self.is_red else 'f')
    
    @classmethod
    def get_yaojiupai(self):
        return [
            p
            for p in [
                Pai.deserialize(str)
                for str in [
                    "m1",
                    "m9",
                    "p1",
                    "p9",
                    "s1",
                    "s9",
                ]
            ]
        ] + [Pai(suit="z", num=n) for n in range(1, 8)]
        
    @classmethod
    def get_zhongzhangpai(self):
        return [Pai(suit=s,num=i) for  i in range(2,9) for s in ["m","s","p"]]
    
    @classmethod
    def deserialize(cls, str: str) -> "Pai":
        if len(str) < 2 or len(str) > 3:
            raise ValueError("文字数は2~3文字にしてください")
        
        try:
            suit = str[0]  
            num = int(str[1])
            is_red = len(str) == 3 and str[2] == "t"
            return cls(suit=suit, num=num, is_red=is_red)
        except Exception as e:
            print("error")  
            raise ValueError(f"正しい文字を指定してください。与えられた文字:{str}")
    
    def get_name(self):
        if self.suit=="z":
            zi={
                1:"東",
                2:"南",
                3:"西",
                4:"北",
                5:"白",
                6:"發",
                7:"中",
                
            }
            return zi[self.num]
        elif self.suit in ["m","p","s"]:
            suit={
                "m":"萬",
                "p":"筒",
                "s":"索"
            }
            shu={
                1:"一",
                2:"二",
                3:"三",
                4:"四",
                5:"五",
                6:"六",
                7:"七",
                8:"八",
                9:"九",
            }
            return f"{shu[self.num]}{suit[self.suit]}"
        else :
            return "裏牌"


        
    
    