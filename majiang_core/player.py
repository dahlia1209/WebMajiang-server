from pydantic import BaseModel, Field,AliasChoices
from typing import List, Optional, Any, Union,Dict
from .board import Board,Kaiju
from models.user import User

class Msg(BaseModel):
    kaiju: Optional[Kaiju] = None
    qipai: Optional[Any] = None
    zimo: Optional[Any] = None
    dapai: Optional[Any] = None
    fulou: Optional[Any] = None
    gang: Optional[Any] = None
    gangzimo: Optional[Any] = None
    kaigang: Optional[Any] = None
    hule: Optional[Any] = None
    pingju: Optional[Any] = None
    jieju: Optional[Any] = None

class Player(BaseModel):
    model: Board = Field(validation_alias=AliasChoices('model', '_model'))
    callback: Optional[Any] = Field(default=None, validation_alias=AliasChoices('callback', '_callback'))
    view: Optional[Any] = Field(default=None, validation_alias=AliasChoices('view', '_view'))
    menfeng: Optional[int] = Field(default=None, validation_alias=AliasChoices('menfeng', '_menfeng'))
    id: Optional[int] = Field(default=None, validation_alias=AliasChoices('id', '_id'))
    rule: Optional[Any] = Field(default=None, validation_alias=AliasChoices('rule', '_rule'))
    diyizimo: Optional[bool] = Field(default=None, validation_alias=AliasChoices('diyizimo', '_diyizimo'))
    n_gang: Optional[int] = Field(default=None, validation_alias=AliasChoices('n_gang', '_n_gang'))
    neng_rong: Optional[bool] = Field(default=None, validation_alias=AliasChoices('neng_rong', '_neng_rong'))
    paipu: Optional[Any] = Field(default=None, validation_alias=AliasChoices('paipu', '_paipu'))
    node: Optional[Dict[str, Any]] = Field(default=None, validation_alias=AliasChoices('node', '_node'))
    mianzi: Optional[Any] = Field(default=None, validation_alias=AliasChoices('mianzi', '_mianzi'))
    sound_on: Optional[Any] = Field(default=None, validation_alias=AliasChoices('sound_on', 'sound_on'))
    audio: Optional[Any] = Field(default=None, validation_alias=AliasChoices('audio', '_audio'))
    show_button: bool = Field(default=False, validation_alias=AliasChoices('show_button', '_show_button'))
    default_reply: Optional[Any] = Field(default=None, validation_alias=AliasChoices('default_reply', '_default_reply'))
    timer_id: Optional[Any] = Field(default=None, validation_alias=AliasChoices('timer_id', '_timer_id'))
    user: Optional[User] = Field(default=None, validation_alias=AliasChoices('user', '_user'))
