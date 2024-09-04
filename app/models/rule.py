from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Literal, List
from .pai import Pai


class Rule(BaseModel):
    red_pais: List[Pai] = Field(default=[])

    @field_validator('red_pais')
    @classmethod
    def check_red_pais(cls,pais:List[Pai]):
        for p in pais:
            if p.is_red==False:
                raise ValueError(f"次の牌は赤ドラではありません:{p}")
        return pais
    