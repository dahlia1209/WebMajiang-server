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
    
    