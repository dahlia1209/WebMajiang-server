from pydantic import BaseModel, Field, ConfigDict,PrivateAttr
from typing import List, Optional
import random
from .pai import Pai

class He(BaseModel):
    pais:List[Pai]=Field(default=[])
    lizhi_num:int=Field(default=-1)
    
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