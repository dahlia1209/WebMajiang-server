from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional

Feng = Literal["東", "南", "西", "北"]

PaiSuit = Literal["b","m", "p", "s", "z"]

PlayerAction = Literal["zimo", "dapai", "fulou", "hule", "lingshangzimo","kaiju","qipai"]

Position=Literal["main","xiajia","duimian","shangjia"]

PlayerStatus=Literal["thinking","ready"]

Combination=Literal["shunzi","kezi","duizi","tazi","gangzi"]

