import pytest
from pydantic import ValidationError
from app.models.pai import Pai

def test_valid_pai_creation():
    # 萬子（マンズ）のテスト
    manzu = Pai(suit='m', num=3)
    assert manzu.suit == 'm'
    assert manzu.num == 3
    assert not manzu.is_red

    # 筒子（ピンズ）のテスト
    pinzu = Pai(suit='p', num=7)
    assert pinzu.suit == 'p'
    assert pinzu.num == 7
    assert not pinzu.is_red

    # 索子（ソーズ）のテスト
    souzu = Pai(suit='s', num=1)
    assert souzu.suit == 's'
    assert souzu.num == 1
    assert not souzu.is_red

    # 字牌のテスト
    jihai_east = Pai(suit='z', num=1)
    assert jihai_east.suit == 'z'
    assert jihai_east.num == 1
    assert not jihai_east.is_red

    jihai_white = Pai(suit='z', num=5)
    assert jihai_white.suit == 'z'
    assert jihai_white.num == 5
    assert not jihai_white.is_red

    # 赤ドラのテスト
    red_five_man = Pai(suit='m', num=5, is_red=True)
    assert red_five_man.suit == 'm'
    assert red_five_man.num == 5
    assert red_five_man.is_red

def test_invalid_suit():
    with pytest.raises(ValidationError):
        Pai(suit='x', num=1)

def test_invalid_number_for_normal_suit():
    with pytest.raises(ValidationError):
        Pai(suit='m', num=10)

def test_invalid_number_for_honor_suit():
    with pytest.raises(ValidationError):
        Pai(suit='z', num=8)

def test_invalid_red_dora():
    with pytest.raises(ValidationError):
        Pai(suit='m', num=1, is_red=True)
    
    with pytest.raises(ValidationError):
        Pai(suit='z', num=5, is_red=True)

def test_red_five():
    pai = Pai(suit='p', num=5, is_red=True)
    assert pai.is_red

def test_honor_tiles():
    honor_tiles = [('z', i) for i in range(1, 8)]
    expected_names = ['東', '南', '西', '北', '白', '發', '中']
    for (suit, num), expected_name in zip(honor_tiles, expected_names):
        pai = Pai(suit=suit, num=num)

def test_str_representation():
    pai = Pai(suit='s', num=7)

def test_repr_representation():
    pai = Pai(suit='m', num=1)
    assert repr(pai) == "Pai(suit='m', num=1, is_red=False)"

def test_equality():
    pai1 = Pai(suit='p', num=5)
    pai2 = Pai(suit='p', num=5)
    pai3 = Pai(suit='s', num=5)
    pai4 = Pai(suit='p', num=5, is_red=True)
    assert pai1 == pai2
    assert pai1 != pai3
    assert pai1 != pai4

def test_is_red():
    red_dora = Pai(suit='m', num=5, is_red=True)
    normal_pai = Pai(suit='m', num=5)
    assert red_dora.is_red
    assert not normal_pai.is_red

def test_serialize_and_deserialize():
    pai=Pai(suit="m",num=5)
    assert pai.serialize()=="m5f"
    pai=Pai(suit="m",num=5,is_red=True)
    assert pai.serialize()=="m5t"
    pai=Pai(suit="b",num=0)
    assert pai.serialize()=="b0f"
    
    pai=Pai.deserialize("m5f")
    assert pai==Pai(suit="m",num=5)
    pai=Pai.deserialize("m5")
    assert pai==Pai(suit="m",num=5)
    pai=Pai.deserialize("m5t")
    assert pai==Pai(suit="m",num=5,is_red=True)
    pai=Pai.deserialize("b0")
    assert pai==Pai(suit="b",num=0)
