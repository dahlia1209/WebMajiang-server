from typing import List, Dict, Any,Optional,Literal,Union
from pydantic import BaseModel,EmailStr, ConfigDict,Field
from fastapi import WebSocket
from faker import Faker

class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,from_attributes=True)
    uid: str
    name: str
    client_socket: WebSocket
    room_id: Optional[str]=None

    @staticmethod
    def generate_fake_name(locale="ja_JP"):
        fake = Faker(locale)
        return fake.name()
        
    def add_room(self, room_uid: str):
        if room_uid not in self.room_id:
            self.room_id=room_uid
        else:
            raise Exception(f"User {self.uid} is already in room {room_uid}")
    
    def remove_room(self, room_uid: str):
        if room_uid in self.room_id:
            self.room_id=None
        else:
            raise Exception(f"User {self.uid} is not in room {room_uid}")