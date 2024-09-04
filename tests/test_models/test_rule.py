import pytest
from pydantic import ValidationError
from app.models.rule import Rule
from app.models.pai import Pai

def test_rule_initialization():
    rule = Rule()
    assert len(rule.red_pais)==0
    assert rule.red_pais==[]

def test_rule_set_red_pais():
    rule = Rule(red_pais=[Pai(num=5,suit='m',is_red=True),Pai(num=5,suit='p',is_red=True),Pai(num=5,suit='s',is_red=True)])
    assert len(rule.red_pais)==3
    assert rule.red_pais[0]==Pai(num=5,suit='m',is_red=True)
    assert rule.red_pais[1]==Pai(num=5,suit='p',is_red=True)
    assert rule.red_pais[2]==Pai(num=5,suit='s',is_red=True)
    
    with pytest.raises(ValueError):
        Rule(red_pais=[Pai(num=5,suit='m')])
        
