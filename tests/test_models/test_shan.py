import pytest
from app.models.shan import Pai, Shan

def create_pais(pai_strings):
    return [Pai(suit=s[1], num=int(s[0])) for i, s in enumerate(pai_strings)]


def test_shan_initialization():
    shan = Shan()
    assert len(shan.pais) == 0
    assert shan.pais == []
    
    pais=[]
    for _ in range(0,70):
        pais.append(Pai(num=1,suit='m'))
    shan = Shan(pais=pais)
    assert len(shan.pais) == 70
    
    with pytest.raises(ValueError):
        pais=[]
        for _ in range(0,71):
            pais.append(Pai(num=1,suit='m'))
        shan = Shan(pais=pais)

def test_pop():
    shan = Shan(pais=create_pais(['1m','2m','3m']))
    assert len(shan.pais) == 3
    pai=shan.pop()
    assert len(shan.pais) == 2
    assert pai==Pai(num=3,suit='m')
    assert shan.pais[0]==Pai(num=1,suit='m')
    assert shan.pais[1]==Pai(num=2,suit='m')
    