from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from faker import Faker
import uuid

class User(BaseModel):
    name:str
    id:str
    email:str
    
    @staticmethod
    def guest():
        fake_jp = Faker('ja_JP')
        return User(name=fake_jp.name(),id=str(uuid.uuid4()),email=fake_jp.email())
        