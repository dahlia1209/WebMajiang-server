import pytest
from app.models.he import He
from app.models.pai import Pai


def create_pais(pai_strings):
    return [Pai(suit=s[1], num=int(s[0])) for i, s in enumerate(pai_strings)]

def test_he_init():
    he = He()
    assert len(he.pais) == 0


def test_add_pai():
    he = He()
    he.add_pai(Pai(num=1, suit="m"))
    assert len(he.pais) == 1
    assert he.pais[0] == Pai(num=1, suit="m")


def test_remove_current_pai():
    he = He(pais=create_pais(["1m", "2m", "3m", "4m"]))
    pai = he.pop()
    assert len(he.pais) == 3
    assert pai == Pai(num=4, suit="m")
