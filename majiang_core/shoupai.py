from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field, field_validator, AliasChoices, ConfigDict
import re
import json

class BingPai(BaseModel):
    u: int
    m: List[int] = Field(default_factory=lambda: [0] * 10)
    p: List[int] = Field(default_factory=lambda: [0] * 10)
    s: List[int] = Field(default_factory=lambda: [0] * 10)
    z: List[int] = Field(default_factory=lambda: [0] * 8)

    def __getitem__(self, index: Union[str, int]) -> Union[int, List[int]]:
        if index == "_":
            return self.u
        elif index == "m":
            return self.m
        elif index == "p":
            return self.p
        elif index == "s":
            return self.s
        elif index == "z":
            return self.z
        else:
            raise KeyError("Invalid key")

    def __setitem__(self, index: Union[str, int], value: Union[int, List[int]]):
        if index == "_":
            self.u = value
        elif index == "m":
            self.m = value
        elif index == "p":
            self.p = value
        elif index == "s":
            self.s = value
        elif index == "z":
            self.z = value
        else:
            raise KeyError("Invalid key")


class Shoupai(BaseModel):
    bingpai: BingPai = Field(default=None,alias="_bingpai")
    fulou_pai: List[str] = Field(default_factory=list, alias="_fulou")
    zimo_pai: Optional[str] = Field(default=None, alias="_zimo")
    lizhi: bool = Field(default=False, alias="_lizhi")

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @staticmethod
    def valid_pai(p: str) -> Optional[str]:
        import re

        if re.match(r"^(?:[mps]\d|z[1-7])_?\*?[\+\=\-]?$", p):
            return p
        return None

    @staticmethod
    def valid_mianzi(m: str) -> Optional[str]:
        import re

        if re.match(r"^z.*[089]", m):
            return None

        h = m.replace("0", "5")

        if re.match(r"^[mpsz](\d)\1\1[\+\=\-]\1?$", h):
            return m.replace(r"([mps])05", r"\1" + "50")

        elif re.match(r"^[mpsz](\d)\1\1\1[\+\=\-]?$", h):
            mmatch = re.findall(r"\d(?![\+\=\-])", m)
            if not mmatch:
                return None
            return (
                m[0]
                + "".join(sorted(mmatch, reverse=True))
                + (re.findall(r"\d[\+\=\-]$", m) or [""])[0]
            )

        elif re.match(r"^[mps]\d+\-\d*$", h):
            hongpai = re.findall("0", m)
            nnmatch = re.findall(r"\d", h)
            if not nnmatch:
                return None
            nn = sorted(nnmatch)
            if (
                len(nn) != 3
                or int(nn[0]) + 1 != int(nn[1])
                or int(nn[1]) + 1 != int(nn[2])
            ):
                return None
            h = h[0] + "".join(sorted(re.findall(r"\d[\+\=\-]?", h)))
            return h.replace("5", "0") if hongpai else h

        return None

    @field_validator("bingpai", mode="before")
    def set_defaultbingpai(cls, v):
        return v or BingPai(u=0, m=[0] * 10, p=[0] * 10, s=[0] * 10, z=[0] * 8)

    def __init__(
        self,
        qipai: Optional[List[str]] = None,
        **data,
    ):
        super().__init__(**data)
        
        if self.bingpai is None:
            self.bingpai = BingPai(u=0, m=[0] * 10, p=[0] * 10, s=[0] * 10, z=[0] * 8)

        if qipai is None:
            qipai = []

        for p in qipai:
            if p == "_":
                self.bingpai.u += 1
                continue

            validated_pai = self.valid_pai(p)
            if not validated_pai:
                raise ValueError(f"Invalid tile: {p}")

            s = validated_pai[0]
            n = int(validated_pai[1])

            if self.bingpai[s][n] == 4:
                raise ValueError(f"Too many tiles of {p}")

            self.bingpai[s][n] += 1
            if s != "z" and n == 0:
                self.bingpai[s][5] += 1

    def to_string(self) -> str:
        paistr = ""

        for s in ["m", "p", "s", "z"]:
            suitstr = s
            bingpai = getattr(self.bingpai, s)
            n_hongpai = 0 if s == "z" else bingpai[0]
            for n in range(1, len(bingpai)):
                n_pai = bingpai[n]
                if self.zimo_pai:
                    if s + str(n) == self.zimo_pai:
                        n_pai -= 1
                    if n == 5 and s + "0" == self.zimo_pai:
                        n_pai -= 1
                        n_hongpai -= 1
                for _ in range(n_pai):
                    if n == 5 and n_hongpai > 0:
                        suitstr += "0"
                        n_hongpai -= 1
                    else:
                        suitstr += str(n)
            if len(suitstr) > 1:
                paistr += suitstr

        if self.zimo_pai and len(self.zimo_pai) <= 2:
            paistr += self.zimo_pai
        if self.lizhi:
            paistr += "*"

        for m in self.fulou_pai:
            paistr += "," + m
        if self.zimo_pai and len(self.zimo_pai) > 2:
            paistr += ","
        return paistr

    def zimo(self, p: str, check: bool = True) -> "Shoupai":
        if check and self.zimo_pai:
            raise ValueError(f"{self.model_dump_json()}, {p}")

        if p == "_":
            self.bingpai.u += 1
            self.zimo_pai = p
        else:
            if not Shoupai.valid_pai(p):
                raise ValueError(p)
            s, n = p[0], int(p[1])
            bingpai = self.bingpai[s]
            if bingpai[n] == 4:
                raise ValueError(f"{self.model_dump_json()}, {p}")
            bingpai[n] += 1
            if n == 0:
                if bingpai[5] == 4:
                    raise ValueError(f"{self.model_dump_json()}, {p}")
                bingpai[5] += 1
            self.zimo_pai = f"{s}{n}"

        return self

    def decrease(self, s: str, n: int):
        bingpai = getattr(self.bingpai, s)
        if bingpai[n] == 0 or (n == 5 and bingpai[0] == bingpai[5]):
            if self.bingpai.u == 0:
                raise ValueError(f"{self.model_dump_json()}, {s + str(n)}")
            self.bingpai.u -= 1
        else:
            bingpai[n] -= 1
            if n == 0:
                bingpai[5] -= 1

    def dapai(self, p: str, check: bool = True) -> "Shoupai":
        if check and not self.zimo_pai:
            raise ValueError(f"{self.model_dump_json()}, {p}")
        if not Shoupai.valid_pai(p):
            raise ValueError(p)
        s, n = p[0], int(p[1])
        self.decrease(s, n)
        self.zimo_pai = None
        if p.endswith("*"):
            self.lizhi = True
        return self

    def fulou(self, m: str, check=True):
        if check and self.zimo_pai:
            raise ValueError(f"{json.dumps(self.__dict__)},{m}")
        
        if m != Shoupai.valid_mianzi(m):
            raise ValueError(m)
        
        if re.search(r'\d{4}$', m):
            raise ValueError(f"{json.dumps(self.__dict__)},{m}")
        
        if re.search(r'\d{3}[\+\=\-]\d$', m):
            raise ValueError(f"{json.dumps(self.__dict__)},{m}")
        
        s = m[0]
        if s not in 'mpsz':
            raise ValueError(f"Invalid suit: {s}")
        
        for n in re.findall(r'\d(?![\+\=\-])', m):
            self.decrease(s, int(n))
        
        self.fulou_pai.append(m)
        
        if not re.search(r'\d{4}', m):
            self.zimo_pai = m
        
        return self
    
    def clone(self) -> 'Shoupai':
        shoupai = Shoupai()

        shoupai.bingpai = BingPai(
            u=self.bingpai.u,
            m=self.bingpai.m.copy(),
            p=self.bingpai.p.copy(),
            s=self.bingpai.s.copy(),
            z=self.bingpai.z.copy()
        )
        shoupai.fulou_pai = self.fulou_pai.copy()
        shoupai.zimo_pai = self.zimo_pai
        shoupai.lizhi = self.lizhi

        return shoupai
    
    def to_string(self) -> str:
        paistr = '_' * (self.bingpai.u + (1 if self.zimo_pai == '_' else 0))
        
        for s in ['m', 'p', 's', 'z']:
            suitstr = s
            bingpai = getattr(self.bingpai, s)
            n_hongpai = 0 if s == 'z' else bingpai[0]
            for n in range(1, len(bingpai)):
                n_pai = bingpai[n]
                if self.zimo_pai:
                    if s + str(n) == self.zimo_pai:
                        n_pai -= 1
                    if n == 5 and s + "0" == self.zimo_pai:
                        n_pai -= 1
                        n_hongpai -= 1
                for _ in range(n_pai):
                    if n == 5 and n_hongpai > 0:
                        suitstr += "0"
                        n_hongpai -= 1
                    else:
                        suitstr += str(n)
            if len(suitstr) > 1:
                paistr += suitstr
        
        if self.zimo_pai and len(self.zimo_pai) <= 2:
            paistr += self.zimo_pai
        if self.lizhi:
            paistr += "*"
        
        for m in self.fulou_pai:
            paistr += "," + m
        if self.zimo_pai and len(self.zimo_pai) > 2:
            paistr += ","
        
        return paistr
    
    def gang(self, m: str, check: bool = True) -> 'Shoupai':
        if check and not self.zimo_pai:
            raise ValueError(f"{self},{m}")
        if check and self.zimo_pai and len(self.zimo_pai) > 2:
            raise ValueError(f"{self},{m}")
        if m != Shoupai.valid_mianzi(m):
            raise ValueError(m)

        s = m[0]
        if re.match(r'\d{4}$', m):
            for n in re.findall(r'\d', m):
                self.decrease(s, int(n))
            self.fulou_pai.append(m)
        elif re.match(r'\d{3}[\+\=\-]\d$', m):
            m1 = m[:5]
            try:
                i = self.fulou_pai.index(m1)
                self.fulou_pai[i] = m
                self.decrease(s, int(m[-1]))
            except ValueError:
                raise ValueError(f"{self},{m}")
        else:
            raise ValueError(f"{self},{m}")

        self.zimo_pai = None
        return self