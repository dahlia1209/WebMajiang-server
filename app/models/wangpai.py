from pydantic import BaseModel, Field, PrivateAttr, field_validator
from typing import List, Optional
from .pai import Pai


class Wangpai(BaseModel):
    lingshangpai: List[Pai] = Field(default=[])
    baopai: List[Pai] = Field(default=[])
    flipped_baopai: List[bool] = Field(default=[])
    libaopai: List[Pai] = Field(default=[])

    def pop_lingshangpai(self):
        if self.lingshangpai:
            return self.lingshangpai.pop(0)
        else:
            raise ValueError("嶺上牌がありません。")

    def flip_baopai(self):
        if self.flipped_baopai[-1]:
            raise ValueError("カンドラめくりができません")
        for i, is_flipped in enumerate(self.flipped_baopai):
            if is_flipped == False:
                self.flipped_baopai[i] = True
                return

    @field_validator("lingshangpai")
    @classmethod
    def check_lingshangzimo(clas, v: List[Pai]):
        if len(v) != 4:
            raise ValueError(
                f"嶺上牌は4枚セットしてください。セットされた牌の枚数:{len(v)}"
            )
        return v

    @field_validator("baopai")
    @classmethod
    def check_baopai(clas, v: List[Pai]):
        if len(v) != 5:
            raise ValueError(
                f"ドラ牌は5枚セットしてください。セットされた牌の枚数:{len(v)}"
            )
        return v

    @field_validator("libaopai")
    @classmethod
    def check_libaopai(clas, v: List[Pai]):
        if len(v) != 5:
            raise ValueError(
                f"裏ドラ牌は5枚セットしてください。セットされた牌の枚数:{len(v)}"
            )
        return v

    @field_validator("flipped_baopai")
    @classmethod
    def check_flipped_baopai(clas, v: List[bool]):
        if len(v) != 5:
            raise ValueError(f"flipped_baopai配列の要素は5つです。要素の数:{len(v)}")
        return v
    
    @staticmethod
    def zhenbaopai(pai:Pai):
        if pai.suit in ["m", "p", "s"]:
            if pai.num == 9:
                return Pai(num=1,suit=pai.suit)
            else:
                return Pai(num=pai.num+1,suit=pai.suit)
        elif pai.suit == "z":
            if pai.num == 4:
                return Pai(num=1,suit=pai.suit)
            elif pai.num == 7:
                return Pai(num=5,suit=pai.suit)
            else :
                return Pai(num=pai.num+1,suit=pai.suit)
    
    def get_zhenbaopai(self,baopai:List[Pai]=[]):
        zhenbaopai:List[Pai]=[]
        baopai=self.baopai if baopai==[] else baopai
        for i, is_flipped in enumerate(self.flipped_baopai):
            if is_flipped:
                pai=Wangpai.zhenbaopai(baopai[i])
                zhenbaopai.append(pai)
            else:
                break
        return zhenbaopai

    def get_zhenbaopai_in_hule(self,is_lizhi:bool):
        zhenbaopai:List[Pai]=self.get_zhenbaopai()
        if is_lizhi:
            zhenbaopai.extend(self.get_zhenbaopai(self.libaopai))
        return zhenbaopai
       
