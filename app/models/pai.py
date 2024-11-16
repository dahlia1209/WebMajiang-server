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
    def deserialize(cls, string: str) -> "Pai":
        if len(string) < 2 or len(string) > 3:
            raise ValueError("文字数は2~3文字にしてください")
        
        try:
            suit = string[0]  # PaiSuitは文字列リテラル型として定義されていると仮定
            num = int(string[1])
            is_red = len(string) == 3 and string[2] == "t"
            return cls(suit=suit, num=num, is_red=is_red)
        except Exception as e:
            print("error")  # または logging.error("error") を使用
            raise ValueError(f"正しい文字を指定してください。与えられた文字:{string}")
        
    
    