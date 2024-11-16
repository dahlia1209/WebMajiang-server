import pytest
from app.models.user import User
from faker import Faker
import uuid

# def test_user_init():
#     fake_jp = Faker('ja_JP')
#     name=fake_jp.name()
#     email=fake_jp.email()
#     id=str(uuid.uuid4())
    
#     user=User(name=name,user_id=id,email=email)
#     assert user==User(name=name,user_id=id,email=email)
    
# def test_guest():
#     user=User.guest()
#     assert  isinstance(user.name,str)
#     assert  isinstance(user.email,str)
#     assert  isinstance(user.user_id,str)