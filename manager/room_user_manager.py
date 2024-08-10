from typing import List, Dict, Any,Optional,Literal,Union
from pydantic import BaseModel,EmailStr, ConfigDict,Field
from models.models import  Room
from models.user import User
from fastapi import WebSocket
from majiang_core.game import Game
import uuid,random


class RoomUserManager:
    model_config = ConfigDict(arbitrary_types_allowed=True)
    def __init__(self):
        self.rooms = {}
        self.users = {}

    def create_user(self, uid: str, name: str, websocket: WebSocket) -> User:
        if uid not in self.users:
            user = User(uid=uid, name=name, client_socket=websocket)
            self.users[uid] = user
            return user
        else:
            raise Exception("User already exists")

    def create_room(self,created_user:User,name:str=None, uid: str=None, game: Game=None) -> Room:
        if uid is None:
            uid = str(uuid.uuid4())
            created_user.room_id=uid
        if name is None:
            name=Room.generate_fake_name()
        if uid not in self.rooms:
            # game = Game(game_id=game_id, status=game_status)
            room = Room(uid=uid, game=game,name=name,users=[created_user.uid],host_user_id=created_user.uid)
            self.rooms[uid] = room
            return room
        else:
            raise Exception("Room already exists")

    def add_user_to_room(self, user_uid: str, room_uid: str):
        user = self.users.get(user_uid)
        room = self.rooms.get(room_uid)
        if user and room:
            room.add_user(user_uid)
            user.room_id=room_uid
        else:
            raise Exception("User or Room does not exist")

    def remove_user_from_room(self, user_uid: str, room_uid: str):
        user = self.users.get(user_uid)
        room = self.rooms.get(room_uid)
        if user and room:
            room.remove_user(user_uid)
            user.room_id=None
        else:
            raise Exception("User or Room does not exist")

    def get_room_users(self, room_uid: str) -> List[User]:
        room = self.rooms.get(room_uid)
        if room:
            return [self.users[user_uid] for user_uid in room.users]
        else:
            raise Exception("Room does not exist")

    def get_user_rooms(self, user_uid: str) -> Room:
        user = self.users.get(user_uid)
        if user and user.room_id:
            return self.rooms.get(user.room_id)
        else:
            return None

    def delete_user(self, user_uid: str):
        user = self.users.pop(user_uid, None)
        if user:
            self.remove_user_from_room(user_uid, user.room_uid)
        else:
            raise Exception("User does not exist")

    def delete_room(self, room_uid: str):
        room = self.rooms.pop(room_uid, None)
        if room:
            for user_uid in room.users:
                self.remove_user_from_room(user_uid, room_uid)
        else:
            raise Exception("Room does not exist")
        
    def get_user(self, user_uid: str) -> Optional[User]:
        return self.users.get(user_uid)

    def get_room(self,  room_uid: str = None, user_uid: str = None) -> Optional[Room]:
        if room_uid:
            return self.rooms.get(room_uid)
        elif user_uid:
            user = self.users.get(user_uid)
            if user and user.room_id:
                return self.rooms.get(user.room_id)
        return None