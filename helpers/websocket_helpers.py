from models.models import WsMessage,Token,Room
from models.user import User
from manager.connection_manager import ConnectionManager
from manager.room_user_manager import RoomUserManager


def authenticate_and_manage_user(verified_token:Token, websocket, room_user_manager:RoomUserManager):
    user = room_user_manager.get_user(verified_token.sub)
    if user is None:
        user = room_user_manager.create_user(
            verified_token.sub,
            verified_token.name,
            websocket,
        )
    else:
        user.client_socket = websocket
    return user

def manage_game_room(user:User, room_user_manager:RoomUserManager):
    room = room_user_manager.get_room(user.room_id)
    if room is None:
        room = get_or_create_room(room_user_manager, user)
        # room_user_manager.add_user_to_room(user.uid, room.uid)
    return room

def get_or_create_room(room_user_manager:RoomUserManager, created_user:User):
    if room_user_manager.rooms:
        return list(room_user_manager.rooms.values())[0]
    return room_user_manager.create_room(created_user=created_user)

async def notify_game_start(room:Room, connection_manager:ConnectionManager, room_user_manager:RoomUserManager):
    for user_uid in room.users:
        user = room_user_manager.get_user(user_uid)
        message = WsMessage(
            event_name="START",
            content={
                "user": {"uid": user.uid, "name": user.name},
                "room": {"uid": room.uid, "name": room.name, "users": room.users},
            },
        )
        await connection_manager.send_personal_message(
            message=message, websocket=user.client_socket
        )