from pydantic import BaseModel
from typing import Union, Optional,Literal

class WsMessage(BaseModel):
    event_name: Literal["HELLO", "ROOM", "START", "END", "ERROR", "disconnect","GAME"]
    content: Union[str, dict, int]=""