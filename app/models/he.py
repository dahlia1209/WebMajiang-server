from pydantic import BaseModel, Field, ConfigDict,PrivateAttr
from typing import List, Optional
import random
from .pai import Pai

class He(BaseModel):
    pais:List[Pai]=Field(default=[])
    pai_id:List[int]=Field(default=[])
    lizhi_id:int=Field(default=-1)
    
    def do_lizhi(self,pai:Pai,pai_id:int):
        self.do_dapai(pai,pai_id)
        self.lizhi_id=pai_id
    
    def do_dapai(self,pai:Pai,pai_id:int):
        self.pais.append(pai)
        self.pai_id.append(pai_id)
    
    def get_last_pai_id(self):
        pai_id=-1
        if self.pai_id:
            pai_id=self.pai_id[-1]
        return pai_id
    
    def add_pai(self,pai:Pai):
        self.pais.append(pai)
    
    def pop(self):
        pai=self.pais.pop()
        return pai
    
    def init(self):
        self.pais=[]
        
    def get_serialized_he_pai(self):
        if not self.pais :
            return
        return "+".join([p.serialize() for p in  self.pais])