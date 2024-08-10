import re
from .shoupai import Shoupai
from pydantic import BaseModel, Field, AliasChoices
from typing import List, Dict

class He(BaseModel):
    pai: List[str] = Field(default_factory=list,alias="_pai")
    find: Dict[str, bool] = Field(default_factory=dict,alias="_find")

    def dapai(self, p: str):
        if not Shoupai.valid_pai(p):
            raise ValueError(p)
        self.pai.append(re.sub(r'[\+\=\-]$', '', p))
        self.find[p[0] + str(int(p[1]) if p[1] != '0' else 5)] = True
        return self

    def fulou(self, m: str):
        if not Shoupai.valid_mianzi(m):
            raise ValueError(m)
        p = m[0] + re.search(r'\d(?=[\+\=\-])', m).group(0)
        d = re.search(r'[\+\=\-]', m)
        if not d:
            raise ValueError(m)
        if self.pai[-1][:2] != p:
            raise ValueError(m)
        self.pai[-1] += d.group(0)
        return self

    def find_he(self, p: str) -> bool:
        return self.find.get(p[0] + str(int(p[1]) if p[1] != '0' else 5), False)