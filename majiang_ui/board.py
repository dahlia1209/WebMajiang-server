from majiang_core.board import Board as Base
from typing import Any, Optional,List
from pydantic import BaseModel, Field,AliasChoices

class Score(BaseModel):
    model: Optional[Any] = Field(default=None, validation_alias=AliasChoices('model', '_model'))
    view: Optional[Any] = Field(default=None, validation_alias=AliasChoices('view', '_view'))
    viewpoint: Optional[Any] = Field(default=None, validation_alias=AliasChoices('viewpoint', '_viewpoint'))
    root: Optional[Any] = Field(default=None, validation_alias=AliasChoices('root', '_root'))

class View(BaseModel):
    score: Score
    shan: Optional[Any] = None
    shoupai: List[Any] = []
    he: List[Any] = []
    say: List[Any] = []
    dialog: Optional[Any] = None
    summary: Optional[Any] = None
    kaiju: Optional[Any] = None

class Board (Base):
    root: Optional[Any] = Field(default=None, validation_alias=AliasChoices('root', '_root'))
    model: Optional[Any] = Field(default=None, validation_alias=AliasChoices('model', '_model'))
    pai: Optional[Any] = Field(default=None, validation_alias=AliasChoices('pai', '_pai'))
    view: Optional[View] = Field(default=None, validation_alias=AliasChoices('view', '_view'))
    say: Optional[Any] = Field(default=None, validation_alias=AliasChoices('say', '_say'))
    lizhi: Optional[Any] = Field(default=None, validation_alias=AliasChoices('lizhi', '_lizhi'))
    viewpoint: Optional[Any] = Field(default=None)
    sound_on: Optional[Any] = Field(default=None)
    open_shoupai: Optional[Any] = Field(default=None, validation_alias=AliasChoices('open_shoupai', '_open_shoupai'))
    open_he: Optional[Any] = Field(default=None, validation_alias=AliasChoices('open_he', '_open_he'))
    no_player_name: Optional[Any] = Field(default=None, validation_alias=AliasChoices('no_player_name', '_no_player_name'))
    timeout_id: Optional[Any] = Field(default=None, validation_alias=AliasChoices('timeout_id', '_timeout_id'))
    audio: Optional[Any] = Field(default=None, validation_alias=AliasChoices('audio', '_audio'))
    lunban: Optional[Any] = Field(default=None, validation_alias=AliasChoices('lunban', '_lunban'))
