from typing import List, Dict, Any
from pydantic import BaseModel

class Paipu(BaseModel):
    title: str
    player: Any
    qijia: int
    log: List[Any]
    defen: List[int]
    point: List[Any]
    rank: List[Any]

# class Msg(BaseModel):
#     kaiju: Dict[str, Any]
