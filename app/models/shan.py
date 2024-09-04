from pydantic import BaseModel, Field, ConfigDict, PrivateAttr, field_validator
from typing import List, Optional
import random
from .pai import Pai


class Shan(BaseModel):
    pais: List[Pai] = Field(default=[])

    def pop(self) -> Optional[Pai]:
        if len(self.pais) == 0:
            raise ValueError("山牌がありません")
        pai = self.pais.pop()
        return pai

    @field_validator("pais")
    @classmethod
    def check_pais(cls, v:List[Pai]):
        if len(v) > 70:
            raise ValueError("山牌は70枚以下である必要があります。")
        return v
