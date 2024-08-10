from manager.connection_manager import ConnectionManager
from manager.room_user_manager import RoomUserManager
from manager.settings_manager import Settings

room_user_manager = RoomUserManager()
connection_manager =ConnectionManager()
settings =Settings()

def get_room_user_manager():
    return room_user_manager

def get_connection_manager():
    return connection_manager

def get_settings():
    return settings