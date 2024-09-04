from app.models.pai import Pai
from app.models.shoupai import Shoupai
from pydantic import BaseModel

class ScoringService(BaseModel):
    shoupai:Shoupai
    
    def calculate_fu(self):
        pass