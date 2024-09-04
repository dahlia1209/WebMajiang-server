from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional

Feng = Literal["東", "南", "西", "北"]

PaiSuit = Literal["m", "p", "s", "z"]

PlayerAction = Literal["zimo", "dapai", "fulou", "hule", "lingshangzimo"]

