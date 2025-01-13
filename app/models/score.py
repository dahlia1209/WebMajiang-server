from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from .pai import Pai
from .type import Feng

# class ScoreProperty(BaseModel):
#     zhuangfeng: Optional[Feng] = None
#     menfeng: Optional[Feng] = None 
#     baopai: Optional[List[Pai]] = None
#     paishu: Optional[int] = None
#     jushu: Optional[int] = None
#     jicun: Optional[int] = None
#     changbang: Optional[int] = None
#     defen: Optional[List[int]] = None

class Score(BaseModel):
    zhuangfeng: Feng = Field(default="東")
    menfeng: List[Feng] = Field(default=["東","南","西","北"])
    baopai: List[Pai] = Field(default_factory=lambda: [Pai(suit="b", num=0)])
    paishu: int = Field(default=70)
    jushu: int = Field(default=1)
    jicun: int = Field(default=0)
    changbang: int = Field(default=0)
    defen: List[int] = Field(default_factory=lambda: [25000, 25000, 25000, 25000])

    @field_validator('baopai')
    @classmethod
    def validate_baopai(cls, baopai: List[Pai]) -> List[Pai]:
        if 0 < len(baopai) <= 5:
            fill_count = 5 - len(baopai)
            return [*baopai, *[Pai(suit="b", num=0) for _ in range(fill_count)]]
        raise ValueError(f"ドラ牌の枚数が正しくありません。1~5枚に設定してください。baopai:{baopai}")

    @field_validator('defen')
    @classmethod
    def validate_defen(cls, defen: List[int]) -> List[int]:
        if len(defen) != 4:
            raise ValueError(f"各プレイヤーの得点を指定してください。defen:{defen}")
        return defen

    def get_jushu_name(self) -> str:
        quotient = (self.jushu - 1) // 4
        remainder = ((self.jushu - 1) % 4) + 1
        
        match quotient:
            case 0:
                return f"東{remainder}局"
            case 1:
                return f"南{remainder}局"
            case 2:
                return f"西{remainder}局"
            case 3:
                return f"北{remainder}局"
            case _:
                raise ValueError(f"局数が正しく設定されていません：{self.jushu}")

    def get_player_feng(self) -> List[Feng]:
        feng_order: List[Feng] = ["東", "南", "西", "北"]
        start_index = feng_order.index(self.menfeng)
        return [*feng_order[start_index:], *feng_order[:start_index]]
    
    def get_zhuangfeng(self)-> Feng:
        if 1<=self.jushu<5:
            return "東"
        elif 5<=self.jushu<9:
            return "南"
        elif 9<=self.jushu<13:
            return "西"
        elif 13<=self.jushu<17:
            return "北"
        else:
            raise ValueError(f"局数の設定が正しくありません。jushu:{self.jushu}")
    
    # def update(self, score: ScoreProperty):
    #     if score.zhuangfeng is not None:
    #         self.zhuangfeng = score.zhuangfeng
    #     if score.menfeng is not None:
    #         self.menfeng = score.menfeng
    #     if score.baopai is not None:
    #         self.baopai = self.validate_baopai(score.baopai)
    #     if score.paishu is not None:
    #         self.paishu = score.paishu
    #     if score.jushu is not None:
    #         self.jushu = score.jushu
    #     if score.jicun is not None:
    #         self.jicun = score.jicun
    #     if score.changbang is not None:
    #         self.changbang = score.changbang
    #     if score.defen is not None:
    #         self.defen = self.validate_defen(score.defen)