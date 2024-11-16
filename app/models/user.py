from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from faker import Faker
import uuid
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    WebSocketException,
    status,
)

class User(BaseModel):
    user_id:str=Field(default=str(uuid.uuid4()))