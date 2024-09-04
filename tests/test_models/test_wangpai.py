import pytest
from app.models.wangpai import Wangpai
from app.models.pai import Pai


def create_pais(pai_strings):
    return [Pai(suit=s[1], num=int(s[0])) for i, s in enumerate(pai_strings)]


def test_wangpai_init():
    # 正しい
    lingshangpai = create_pais(["1m", "2m", "3m", "4m"])
    baopai = create_pais(["1p", "2p", "3p", "4p", "5p"])
    flipped_baopai = [True, False, False, False, False]
    libaopai = create_pais(["1s", "2s", "3s", "4s", "5s"])
    wangpai = Wangpai(
        baopai=baopai,
        lingshangpai=lingshangpai,
        libaopai=libaopai,
        flipped_baopai=flipped_baopai,
    )
    assert len(wangpai.baopai) == 5
    assert len(wangpai.libaopai) == 5
    assert len(wangpai.lingshangpai) == 4

    # 誤り
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=create_pais(["1p", "2p", "3p", "4p"]),
            lingshangpai=lingshangpai,
            libaopai=libaopai,
            flipped_baopai=flipped_baopai,
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=create_pais(["1p", "2p", "3p", "4p", "5p", "6p"]),
            lingshangpai=lingshangpai,
            libaopai=libaopai,
            flipped_baopai=flipped_baopai,
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=baopai,
            lingshangpai=lingshangpai,
            libaopai=libaopai,
            flipped_baopai=[True, False, False, False],
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=baopai,
            lingshangpai=lingshangpai,
            libaopai=libaopai,
            flipped_baopai=[True, False, False, False, False, False],
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=baopai,
            lingshangpai=lingshangpai,
            libaopai=create_pais(["1s", "2s", "3s", "4s"]),
            flipped_baopai=flipped_baopai,
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=baopai,
            lingshangpai=lingshangpai,
            libaopai=create_pais(["1s", "2s", "3s", "4s", "5s", "6s"]),
            flipped_baopai=flipped_baopai,
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=baopai,
            lingshangpai=create_pais(["1m", "2m", "3m"]),
            libaopai=libaopai,
            flipped_baopai=flipped_baopai,
        )
    with pytest.raises(ValueError):
        wangpai = Wangpai(
            baopai=baopai,
            lingshangpai=create_pais(["1m", "2m", "3m", "4m", "5m"]),
            libaopai=libaopai,
            flipped_baopai=flipped_baopai,
        )

def test_pop_lingshangpai():
    lingshangpai = create_pais(["1m", "2m", "3m", "4m"])
    baopai = create_pais(["1p", "2p", "3p", "4p", "5p"])
    flipped_baopai = [True, False, False, False, False]
    libaopai = create_pais(["1s", "2s", "3s", "4s", "5s"])
    wangpai = Wangpai(
        baopai=baopai,
        lingshangpai=lingshangpai,
        libaopai=libaopai,
        flipped_baopai=flipped_baopai,
    )
    pai=wangpai.pop_lingshangpai()
    assert pai==Pai(num=1, suit="m")
    assert len(wangpai.lingshangpai)==3
    
    #3回嶺上ツモ
    for _ in range(3):
        pai=wangpai.lingshangpai[0].model_copy()
        v=wangpai.pop_lingshangpai()
        assert v==pai
    
    #嶺上牌なし
    with pytest.raises(ValueError):
        wangpai.pop_lingshangpai()
        

def test_flip_baopai():
    lingshangpai = create_pais(["1m", "2m", "3m", "4m"])
    baopai = create_pais(["1p", "2p", "3p", "4p", "5p"])
    flipped_baopai = [True, False, False, False, False]
    libaopai = create_pais(["1s", "2s", "3s", "4s", "5s"])
    wangpai = Wangpai(
        baopai=baopai,
        lingshangpai=lingshangpai,
        libaopai=libaopai,
        flipped_baopai=flipped_baopai,
    )
    wangpai.flip_baopai()
    assert len([is_flipped for is_flipped in wangpai.flipped_baopai if is_flipped]) == 2
    wangpai.flip_baopai()
    wangpai.flip_baopai()
    wangpai.flip_baopai()
    assert len([is_flipped for is_flipped in wangpai.flipped_baopai if is_flipped]) == 5
    assert wangpai.baopai[0] == Pai(num=1, suit="p")
    assert wangpai.baopai[1] == Pai(num=2, suit="p")    
    assert wangpai.baopai[2] == Pai(num=3, suit="p")    
    assert wangpai.baopai[3] == Pai(num=4, suit="p")    
    assert wangpai.baopai[4] == Pai(num=5, suit="p")    
    
    with pytest.raises(ValueError):
        wangpai.flip_baopai()


def test_get_zhenbaopai():
    lingshangpai = create_pais(["1m", "2m", "3m", "4m"])
    baopai = create_pais(["1p", "2p", "3p", "4p", "5p"])
    flipped_baopai = [True, False, False, False, False]
    libaopai = create_pais(["1s", "2s", "3s", "4s", "5s"])
    wangpai = Wangpai(
        baopai=baopai,
        lingshangpai=lingshangpai,
        libaopai=libaopai,
        flipped_baopai=flipped_baopai,
    )
    zhenbaopai = wangpai.get_zhenbaopai()
    assert len(zhenbaopai) == 1
    assert zhenbaopai[0]==Pai(num=2, suit="p")
      
    #カンドラめくり*4
    for _ in range(4):
        wangpai.flip_baopai()
    zhenbaopai = wangpai.get_zhenbaopai()
    assert len(zhenbaopai) == 5
    assert zhenbaopai[1]==Pai(num=3, suit="p")  
    assert zhenbaopai[2]==Pai(num=4, suit="p")  
    assert zhenbaopai[3]==Pai(num=5, suit="p")  
    assert zhenbaopai[4]==Pai(num=6, suit="p")

    #折り返しになるドラ牌
    lingshangpai = create_pais(["1m", "2m", "3m", "4m"])
    baopai = create_pais(["9p", "9m", "9s", "4z", "7z"])
    flipped_baopai = [True, False, False, False, False]
    libaopai = create_pais(["1s", "2s", "3s", "4s", "5s"])
    wangpai = Wangpai(
        baopai=baopai,
        lingshangpai=lingshangpai,
        libaopai=libaopai,
        flipped_baopai=flipped_baopai,
    )
    for _ in range(4):
        wangpai.flip_baopai()
    zhenbaopai = wangpai.get_zhenbaopai()
    assert zhenbaopai[0]==Pai(num=1, suit="p")
    assert zhenbaopai[1]==Pai(num=1, suit="m")
    assert zhenbaopai[2]==Pai(num=1, suit="s")
    assert zhenbaopai[3]==Pai(num=1, suit="z")
    assert zhenbaopai[4]==Pai(num=5, suit="z")
    
    #和了後ドラ取得
    lingshangpai = create_pais(["1m", "2m", "3m", "4m"])
    baopai = create_pais(["1p", "2p", "3p", "4p", "5p"])
    flipped_baopai = [True, False, False, False, False]
    libaopai = create_pais(["1s", "2s", "3s", "4s", "5s"])
    wangpai = Wangpai(
        baopai=baopai,
        lingshangpai=lingshangpai,
        libaopai=libaopai,
        flipped_baopai=flipped_baopai,
    )
    for _ in range(4):
        wangpai.flip_baopai()
    zhenbaopai = wangpai.get_zhenbaopai_in_hule(True)
    assert len(zhenbaopai) == 10
    assert zhenbaopai[5]==Pai(num=2, suit="s")  
    assert zhenbaopai[6]==Pai(num=3, suit="s")  
    assert zhenbaopai[7]==Pai(num=4, suit="s")  
    assert zhenbaopai[8]==Pai(num=5, suit="s")
    assert zhenbaopai[9]==Pai(num=6, suit="s")
    
