from typing import List, Dict, Any,Optional,Literal,Union
from pydantic import BaseModel,EmailStr, ConfigDict,Field
from faker import Faker
import random

from majiang_core.game import Game
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

class Token(BaseModel):
    sub: str
    name: Optional[str]
    emails: Optional[List[EmailStr]] = None
    tfp: str
    nonce: str
    scp: str
    azp: str
    ver: str
    iat: int
    aud: str
    exp: int
    iss: str
    nbf: int

class WsMessage(BaseModel):
    event_name: Literal["HELLO", "ROOM", "START", "END", "ERROR", "disconnect","GAME"]
    content: Optional[Union[str, Dict[str, Any], int]] = None


class Room(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid:str
    # room_no:str
    name:str
    game: Optional[Game]=None
    host_user_id: str
    users: List[str] = Field(default_factory=list)
    
    def add_user(self, user_uid: str):
        if len(self.users) < 4:
            self.users.append(user_uid)
        else:
            raise Exception("Room is full")
    
    def remove_user(self, user_uid: str):
        if user_uid in self.users:
            self.users.remove(user_uid)
            
    @staticmethod
    def generate_fake_name(locale="ja_JP"):
        fake = Faker(locale)
        return fake.country()
    
    @staticmethod
    def get_room_no():
        while True:
            n = random.randint(0, 260000 - 1)
            room_no = chr(65 + (n // 10000)) + "{:04}".format(n % 10000)
            return room_no
