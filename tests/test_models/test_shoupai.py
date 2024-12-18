import pytest
from app.models.shoupai import Shoupai, Fulou
from app.models.pai import Pai

# def test_set_zimo():
#     pais = create_pais(
#         ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2p", "3p"]
#     )
#     shoupai=Shoupai(bingpai=pais)
#     zimopai=Pai(suit='m',num=1)
#     shoupai.zimopai=None
#     shoupai.set_zimopai(zimopai)
#     assert shoupai.zimopai == Pai(suit="m", num=1)
#     shoupai.remove_pai_from_zimopai()
#     assert shoupai.zimopai == None

# def test_sort_pai():
#     pais = [
#         Pai(suit="z", num=1),
#         Pai(suit="m", num=8),
#         Pai(suit="m", num=2),
#         Pai(suit="p", num=2),
#         Pai(suit="s", num=6),
#     ]
#     sort_pai = Shoupai.sort_pai(pais)
#     assert sort_pai[0] == Pai(suit="m", num=2)
#     assert sort_pai[1] == Pai(suit="m", num=8)
#     assert sort_pai[2] == Pai(suit="p", num=2)
#     assert sort_pai[3] == Pai(suit="s", num=6)
#     assert sort_pai[4] == Pai(suit="z", num=1)


# def test_remove_pai():
#     pais = create_pais(["1m", "2m", "3m", "4m", "5m", "5m"])
#     zimopai = Pai(num=5, suit="m")
#     shoupai = Shoupai(bingpai=pais, zimopai=zimopai)
#     shoupai.remove_pai_from_zimopai()
#     assert shoupai.zimopai == None
#     assert len(shoupai.bingpai) == 6

#     shoupai.zimopai = Pai(num=5, suit="m")
#     shoupai.remove_pai_from_bingpai(index=3)
#     assert shoupai.zimopai == Pai(num=5, suit="m")
#     assert len(shoupai.bingpai) == 5
#     shoupai.zimo_into_bingpai()
#     assert len(shoupai.bingpai) == 6
#     assert shoupai.zimopai == None


def test_do_chi():
    # 1回目のチー
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai._compute_fulou_candidates()
    fulou=Fulou.deserialize("chi,m1f,m2f+m3f,shangjia")
    shoupai.do_fulou(fulou)
    assert len(shoupai.fulou) == 1

def test_do_peng():
    # 1回目のポン
    pais = create_pais(
        ["1m", "1m", "1m", "3m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai._compute_fulou_candidates()
    fulou=Fulou.deserialize("peng,m3f,m3+m3,shangjia")
    shoupai.do_fulou(fulou)
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="peng",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=3, suit="m"),
            Pai(num=3, suit="m"),
        ],
        position="shangjia"
    )

def test_do_minggang():
    # カン1回目
    pais = create_pais(
        ["1m", "1m", "1m", "3m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai._compute_fulou_candidates()
    fulou=Fulou.deserialize("minggang,m1,m1+m1+m1,duimian")
    shoupai.do_fulou(fulou)
    
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="minggang",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
        ],
        position="duimian"
    )

def test_do_angang():
    # 暗槓1回目
    pais = [Pai.deserialize(s) for s in ["m1", "m1", "m1", "m1", "m3", "m5", "m5", "m5", "p1", "p1", "p1", "p2", "p3"]]
    shoupai = Shoupai(bingpai=pais, zimopai=Pai(suit="m", num=5, is_red=True))
    shoupai._compute_fulou_candidates()
    fulou=Fulou.deserialize("angang,null,m5+m5+m5+m5t,null")
    shoupai.do_fulou(fulou)
    
    # main_fulou_pai = shoupai.compute_fulou_candidates()
    # shoupai.do_fulou(main_fulou_pai[1])
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="angang",
        fuloupais=[Pai.deserialize(s) for s in ["m5", "m5", "m5", "m5t"]],
    )
    assert len(shoupai.bingpai) == 10
    assert shoupai.bingpai == create_pais(
        ["1m", "1m", "1m", "1m", "3m", "1p", "1p", "1p", "2p", "3p"]
    )

    # 暗槓２回目
    shoupai.zimopai = Pai(suit="p", num=1)
    shoupai._compute_fulou_candidates()
    fulou=Fulou.deserialize("angang,null,p1+p1+p1+p1,null")
    shoupai.do_fulou(fulou)
    assert len(shoupai.fulou) == 2
    assert shoupai.fulou[1] == Fulou(
        type="angang",
        fuloupais=[
            Pai(num=1, suit="p"),
            Pai(num=1, suit="p"),
            Pai(num=1, suit="p"),
            Pai(num=1, suit="p"),
        ],
    )


def test_do_jiagang():
    # 加槓1回目
    pais = create_pais(["1m", "1m", "1m", "1m", "3m", "1p", "1p", "1p", "2p", "3p"])
    fulou = Fulou.deserialize("peng,m5,m5+m5,duimian")
    zimopai = Pai(num=5, suit="m", is_red=True)
    shoupai = Shoupai(bingpai=pais, zimopai=zimopai, fulou=[fulou])
    shoupai._compute_fulou_candidates()
    shoupai.do_fulou(fulou.model_copy(update={"type":"jiagang"}))
    assert shoupai.fulou[0] == Fulou(
        type="jiagang", nakipai=Pai(num=5, suit="m"), fuloupais=[Pai.deserialize(s) for s in ["m5", "m5", "m5t"]],position="duimian"
    )


def create_pais(pai_strings):
    return [Pai(suit=s[1], num=int(s[0])) for i, s in enumerate(pai_strings)]


def test_qidui_tenpai():
    # 七対子テンパイ: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 6s 7m
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "6s", "7m"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=7) 


def test_qidui_not_tenpai():
    # 七対子非テンパイ: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 7s 8m
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "7s", "8m"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0


def test_kokushi_tenpai():
    # 国士無双テンパイ: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 7z
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 13
    # assert shoupai.hule_candidates[0]==Pai(suit="m", num=7) 



def test_kokushi_not_tenpai():
    # 国士無双非テンパイ: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 8s
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "8s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0
    # assert shoupai.hule_candidates[0]==Pai(suit="m", num=7) 


# def test_is_shuntsu():
#     # 順子
#     shoupai=Shoupai()
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="m", num=1, is_red=False),
#             Pai(suit="m", num=2, is_red=False),
#             Pai(suit="m", num=3, is_red=False),
#         ]
#     )
#     assert is_shuntsu == True
    
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="m", num=1, is_red=False),
#             Pai(suit="m", num=2, is_red=False),
#             Pai(suit="m", num=4, is_red=False),
#         ]
#     )
#     assert is_shuntsu == False
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="m", num=2, is_red=False),
#             Pai(suit="m", num=3, is_red=False),
#             Pai(suit="m", num=1, is_red=False),
#         ]
#     )
#     assert is_shuntsu == True
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="s", num=1, is_red=False),
#             Pai(suit="m", num=2, is_red=False),
#             Pai(suit="m", num=3, is_red=False),
#         ]
#     )
#     assert is_shuntsu == False
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="p", num=1, is_red=False),
#             Pai(suit="p", num=2, is_red=False),
#             Pai(suit="p", num=3, is_red=False),
#         ]
#     )
#     assert is_shuntsu == True
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="z", num=1, is_red=False),
#             Pai(suit="z", num=2, is_red=False),
#             Pai(suit="z", num=3, is_red=False),
#         ]
#     )
#     assert is_shuntsu == False
#     is_shuntsu = shoupai.is_shunzi(
#         [
#             Pai(suit="z", num=1, is_red=False),
#             Pai(suit="z", num=1, is_red=False),
#             Pai(suit="z", num=1, is_red=False),
#         ]
#     )
#     assert is_shuntsu == False

# def test_is_kezi():
#     # 刻子
#     shoupai=Shoupai()
#     is_kezi = shoupai.is_kezi(
#         [
#             Pai(suit="m", num=1, is_red=False),
#             Pai(suit="m", num=1, is_red=False),
#             Pai(suit="m", num=1, is_red=False),
#         ]
#     )
#     assert is_kezi == True
#     is_kezi = shoupai.is_kezi(
#         [
#             Pai(suit="m", num=1, is_red=False),
#             Pai(suit="m", num=2, is_red=False),
#             Pai(suit="m", num=3, is_red=False),
#         ]
#     )
#     assert is_kezi == False
#     is_kezi = shoupai.is_kezi(
#         [
#             Pai(suit="p", num=9, is_red=False),
#             Pai(suit="p", num=9, is_red=False),
#             Pai(suit="p", num=9, is_red=False),
#         ]
#     )
#     assert is_kezi == True
#     is_kezi = shoupai.is_kezi(
#         [
#             Pai(suit="m", num=9, is_red=False),
#             Pai(suit="p", num=9, is_red=False),
#             Pai(suit="p", num=9, is_red=False),
#         ]
#     )
#     assert is_kezi == False
#     is_kezi = shoupai.is_kezi(
#         [
#             Pai(suit="s", num=9, is_red=False),
#             Pai(suit="s", num=9, is_red=False),
#             Pai(suit="s", num=9, is_red=False),
#         ]
#     )
#     assert is_kezi == True
#     is_kezi = shoupai.is_kezi(
#         [
#             Pai(suit="z", num=7, is_red=False),
#             Pai(suit="z", num=7, is_red=False),
#             Pai(suit="z", num=7, is_red=False),
#         ]
#     )
#     assert is_kezi == True
#     is_kezi = shoupai.is_kezi([Pai(suit="m", num=1, is_red=False)])

# def test_is_dazi():
#     # 搭子
#     shoupai=Shoupai()
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="m", num=1, is_red=False), Pai(suit="m", num=2, is_red=False)]
#     )
#     assert is_dazi == True
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="m", num=1, is_red=False), Pai(suit="m", num=3, is_red=False)]
#     )
#     assert is_dazi == True
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="m", num=2, is_red=False), Pai(suit="m", num=3, is_red=False)]
#     )
#     assert is_dazi == True
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="m", num=9, is_red=False), Pai(suit="m", num=7, is_red=False)]
#     )
#     assert is_dazi == True
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="s", num=9, is_red=False), Pai(suit="s", num=7, is_red=False)]
#     )
#     assert is_dazi == True
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="p", num=9, is_red=False), Pai(suit="p", num=7, is_red=False)]
#     )
#     assert is_dazi == True
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="z", num=7, is_red=False), Pai(suit="z", num=5, is_red=False)]
#     )
#     assert is_dazi == False
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="p", num=7, is_red=False), Pai(suit="p", num=7, is_red=False)]
#     )
#     assert is_dazi == False
#     is_dazi = shoupai.is_tazi(
#         [Pai(suit="p", num=7, is_red=False), Pai(suit="s", num=6, is_red=False)]
#     )
#     assert is_dazi == False
#     is_dazi = shoupai.is_tazi([Pai(suit="p", num=7, is_red=False)])
#     assert is_dazi == False


# def test_is_duizi():
#     # 搭子
#     shoupai=Shoupai()
#     is_duizi = shoupai.is_duizi(
#         [Pai(suit="m", num=1, is_red=False), Pai(suit="m", num=1, is_red=False)]
#     )
#     assert is_duizi == True
#     is_duizi = shoupai.is_duizi(
#         [Pai(suit="m", num=5, is_red=False), Pai(suit="m", num=5, is_red=True)]
#     )
#     assert is_duizi == True
#     is_duizi = shoupai.is_duizi(
#         [Pai(suit="s", num=5, is_red=False), Pai(suit="s", num=5, is_red=False)]
#     )
#     assert is_duizi == True
#     is_duizi = shoupai.is_duizi(
#         [Pai(suit="s", num=5, is_red=False), Pai(suit="s", num=6, is_red=False)]
#     )
#     assert is_duizi == False


# def test_is_gangzi():
#     # 槓子
#     shoupai=Shoupai()
#     # 1
#     pais = create_pais(["1m", "1m", "1m", "1m"])
#     is_gangzi = shoupai.is_gangzi(pais)
#     assert is_gangzi == True
#     # 2
#     pais = create_pais(["1p", "1p", "1p", "1p"])
#     is_gangzi = shoupai.is_gangzi(pais)
#     assert is_gangzi == True
#     # 3
#     pais = create_pais(["1z", "1z", "1z", "1z"])
#     is_gangzi = shoupai.is_gangzi(pais)
#     assert is_gangzi == True
#     # 4
#     pais = create_pais(["1z", "1z", "1z", "2z"])
#     is_gangzi = shoupai.is_gangzi(pais)
#     assert is_gangzi == False


def test_get_mianzi_pai():
    # 1
    pais = create_pais(["1m", "1m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==2
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=1, suit="m")
    assert shoupai.hule_candidates[1].pais[-1] == Pai(num=1, suit="z")
    
    # mianzi_pai = Shoupai.get_mianzi_pai(pais)
    # assert len(mianzi_pai) == 1
    # assert mianzi_pai[0] == Pai(num=1, suit="m")

    # 2
    pais = create_pais(["1m", "2m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==1
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=3, suit="m")

    # 3
    pais = create_pais(["8m", "9m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==1
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=7, suit="m")
    
    # 4
    pais = create_pais(["7m", "9m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==1
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=8, suit="m")
    
    # 5
    pais = create_pais(["7m", "8m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==2
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=6, suit="m")
    assert shoupai.hule_candidates[1].pais[-1] == Pai(num=9, suit="m")
    
    # 6
    pais = create_pais(["1z", "1z","2z", "2z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==2
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=1, suit="z")
    assert shoupai.hule_candidates[1].pais[-1] == Pai(num=2, suit="z")

    # 7
    pais = create_pais(["1z", "2z","3z", "3z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==0


    # 8
    pais = create_pais(["1m", "4m","3z", "3z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==0
    
    # 9
    pais = create_pais(["5m", "6z","3z", "3z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai._compute_xiangting()
    assert len(shoupai.hule_candidates)==0

def test_find_agari_hai():
    # アガリ牌の抽出
    # 1
    pais = create_pais(["1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)

    # 2
    pais = create_pais(["1m", "1m", "3m", "4m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=5)

    # 3
    pais = create_pais(["1m", "1m", "3m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=4)

    # 4
    pais = create_pais(["1m", "1m", "8m", "9m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=7)

    # 5
    pais = create_pais(["1m", "1m", "2m", "2m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=2)

    # 6
    pais = create_pais(["1m", "3m", "4m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=5)

    # 7
    pais = create_pais(["1m", "3m", "5m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=4)

    # 8
    pais = create_pais(["1m", "8m", "9m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=7)

    # 9
    pais = create_pais(["1m", "2m", "2m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=2)
    
    # 11
    pais = create_pais(["1z", "1z", "1m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="z", num=1)

    # 12
    pais = create_pais(["1z", "2z", "3m", "3m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0

    # 13
    pais = create_pais(["2z", "2z", "3m", "6m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0

    # 14
    pais = create_pais(["1s", "2s", "3s", "6s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=6)

    # 15
    pais = create_pais(["1s", "3s", "6z", "2s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="z", num=6)

    # 16
    pais = create_pais(["1s", "2s", "3s", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    # print("xianting,best_combi",xiangting,[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in shoupai.hule_candidates])
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=4)

    # 17
    pais = create_pais(["1s", "2s", "2s", "2s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)

    # 18
    pais = create_pais(["3s", "2s", "2s", "2s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="s", num=4)

    # 19
    pais = create_pais(["3z", "2z", "2z", "2z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="z", num=3)

    # 20
    pais = create_pais(["2z", "2z", "2z", "2z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    # assert xiangting==1

    # 21
    pais = create_pais(["1s", "2s", "3s", "3s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)

    # 22
    pais = create_pais(["3s", "2s", "4s", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="s", num=4)


    # 23
    pais = create_pais(["4s", "2s", "4s", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)

    # 24
    pais = create_pais(["4s", "2s", "4p", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==1

    # 25
    pais = create_pais(["1p", "2p", "3p", "6p", "7p", "9p", "9p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=8)

    # 多面帳1
    pais = create_pais(["2p", "3p", "4p", "5p", "6p", "1z", "1z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=7)

    # 多面帳2
    pais = create_pais(["2p", "3p", "4p", "5p", "6p", "7p", "8p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=8)

    # 多面帳3
    pais = create_pais(["2p", "3p", "4p", "5p", "5p", "6p", "7p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=8)
    # 多面帳4
    pais = create_pais(["2p", "3p", "4p", "4p", "4p", "1z", "1z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="z", num=1)

    # 多面帳5
    pais = create_pais(["2p", "3p", "3p", "3p", "4p", "5p", "6p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 5
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=7)

    # 多面帳6
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "5p", "6p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 6
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[5].pais[-1]==Pai(suit="p", num=7)

    # 多面帳7
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "5p", "6p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 5
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=7)

    # 多面帳8
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "6p", "7p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 6
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=7)
    assert shoupai.hule_candidates[5].pais[-1]==Pai(suit="p", num=8)

    # 多面帳9
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "6p", "8p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=7)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=8)

    # 多面帳10
    pais = create_pais(["3p", "3p", "3p", "5p", "5p", "6p", "7p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=8)

    # 多面帳11
    pais = create_pais(["3p", "3p", "3p", "5p", "6p", "7p", "8p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=8)

    # 多面帳12
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 5
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=6)

    # 多面帳13
    pais = create_pais(["3p", "3p", "4p", "4p", "4p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)

    # 多面帳14
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 7
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[5].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[6].pais[-1]==Pai(suit="p", num=6)

    # 多面帳15
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "4p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 6
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[5].pais[-1]==Pai(suit="p", num=6)

    # 多面帳16
    pais = create_pais(["3p", "3p", "3p", "5p", "7p", "7p", "7p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=6)

    # 多面帳17
    pais = create_pais(["3p", "3p", "4p", "5p", "5p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=6)

    # 多面帳18
    pais = create_pais(["3p", "3p", "4p", "4p", "4p", "4p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==5
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=6)

    # 多面帳19
    pais = create_pais(["3p", "4p", "4p", "4p", "4p", "5p", "6p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==5
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=6)

    # 多面帳Ex
    pais = create_pais(["4p", "4p", "4p", "3p", "4p", "5p", "6p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==5
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[4].pais[-1]==Pai(suit="p", num=6)


def test_compute_fulou_candidates():
    # 副露牌候補セット
    # 1
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    filtered=[f for f in fulou_candidates if f.type=="chi" and f.nakipai==Pai(num=3, suit="m")]
    assert len(filtered) == 3
    assert filtered[0] == Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=2, suit="m"),
        ],
    )
    assert filtered[1] == Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=2, suit="m"),
            Pai(num=4, suit="m"),
        ],
    )
    assert filtered[2] == Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=4, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )

    # 2
    pais = create_pais(["1m", "1m", "1m", "2m", "2m", "3m", "3m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    filtered=[f for f in fulou_candidates if  f.nakipai==Pai(num=1, suit="m")]
    assert len(filtered) == 3
    assert filtered[0] == Fulou(
        type="chi",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[
            Pai(num=2, suit="m"),
            Pai(num=3, suit="m"),
        ],
    )
    assert filtered[1] == Fulou(
        type="peng",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
        ],
    )
    assert filtered[2] == Fulou(
        type="minggang",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[Pai(num=1, suit="m"), Pai(num=1, suit="m"), Pai(num=1, suit="m")],
    )


def test_compute_fulou_candidates_3():
    # 副露牌候補セット
    # 1
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 24

    # 2
    pais = create_pais(["1m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 0
    # 3
    pais = create_pais(["1m", "2m", "5m", "9m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 1
    # 4
    pais = create_pais(["1m", "2m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 2
    assert  Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=2, suit="m"),
        ],
    ) in shoupai.fulou_candidates
    
    assert Fulou(
        type="peng",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )  in shoupai.fulou_candidates
    # 5
    pais = create_pais(["1m", "5m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 2
    assert Fulou(
        type="peng",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    ) in shoupai.fulou_candidates
    assert  Fulou(
        type="minggang",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    ) in shoupai.fulou_candidates
    # 5
    pais = create_pais(["5m", "5m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 3
    assert Fulou(
        type="peng",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    ) in shoupai.fulou_candidates
    assert Fulou(
        type="minggang",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    ) in shoupai.fulou_candidates
    assert Fulou(
        type="angang",
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    ) in shoupai.fulou_candidates


def test_regular_tenpai_ryanmen():
    # 両面待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2s", "3s"]
    )

    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=4)


def test_regular_tenpai_ryanmen_2():
    # 両面待ち
    pais = create_pais(
        ["1m", "3s", "2s", "3m", "6m", "4m", "5m", "8m", "7m", "9m", "1p", "1p", "2m"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=4)
    
def test_regular_tenpai_kanchan():
    # 嵌張待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=2)

def test_regular_tenpai_penchan():
    # 辺張待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "1p", "1p", "1p", "1s", "1s", "8s", "9s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting == 0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=7)


def test_regular_tenpai_tanki():
    # 4面子1雀頭テンパイ（単騎待ち）
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1p", "1s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    

def test_regular_tenpai_with_fulou():
    # 副露ありの4面子1雀頭テンパイ
    bingpai = create_pais(["1m", "2m", "3m", "4m", "5m", "6m", "1p"])
    fulou = [
        Fulou(
            type="chi",
            nakipai=Pai(suit="s", num=3),
            fuloupais=create_pais(["1s", "2s", "3s"]),
        ),
        Fulou(
            type="peng",
            nakipai=Pai(suit="z", num=1),
            fuloupais=create_pais(["1z", "1z", "1z"]),
        ),
    ]
    shoupai = Shoupai(bingpai=bingpai, fulou=fulou)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=1)

def test_regular_not_tenpai_with_fulou():
    # 副露ありの4面子1雀頭非テンパイ
    bingpai = create_pais(["1m", "2m", "3m", "4m", "5m", "1p", "2p"])
    fulou = [
        Fulou(
            type="chi",
            nakipai=Pai(suit="s", num=3),
            fuloupais=create_pais(["1s", "2s", "3s"]),
        ),
        Fulou(
            type="peng",
            nakipai=Pai(suit="z", num=1),
            fuloupais=create_pais(["1z", "1z", "1z"]),
        ),
    ]
    shoupai = Shoupai(bingpai=bingpai, fulou=fulou)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) ==0

def test_qidui_with_fulou():
    # 副露ありの七対子（テンパイにならない）
    bingpai = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p"]
    )
    fulou = [
        Fulou(
            type="chi",
            nakipai=Pai(suit="s", num=3),
            fuloupais=create_pais(["1s", "2s", "3s"]),
        )
    ]
    shoupai = Shoupai(bingpai=bingpai, fulou=fulou)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==2
    assert len(shoupai.hule_candidates) ==0
    
def test_kokushi_with_fulou():
    # 副露ありの国士無双（テンパイにならない）
    bingpai = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z" ]
    )
    fulou = [
        Fulou(
            type="chi",
            nakipai=Pai(suit="s", num=3),
            fuloupais=create_pais(["1s", "2s", "3s"]),
        )
    ]
    shoupai = Shoupai(bingpai=bingpai, fulou=fulou)
    xiangting = shoupai._compute_xiangting()
    assert xiangting==6
    assert len(shoupai.hule_candidates) ==0

def test_chiitoitsu_tenpai():
    # 七対子テンパイ（チートイツ）: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 6s 7z
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "6s", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai._compute_xiangting()
    assert xiangting == 0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="z", num=7) 

def test_kokushi_13_way_tenpai():
    # 国士無双13面待ち: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 7z
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting=shoupai._compute_xiangting()
    assert xiangting == 0
    assert len(shoupai.hule_candidates) == 13
   
def test_compute_fulou_candidates_2():
    pais = create_pais(
        ["1m", "1m", "1m", "2m","3m","4m","5m","6m","7m","8m","9m","9m","9m"]
    )
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai._compute_fulou_candidates()
    # [print(f.model_dump_json()) for f in fulou_candidates]
    assert len(fulou_candidates)==25
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=1),fuloupais=create_pais(["2m","3m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=2),fuloupais=create_pais(["1m","3m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=2),fuloupais=create_pais(["3m","4m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=3),fuloupais=create_pais(["1m","2m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=3),fuloupais=create_pais(["2m","4m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=3),fuloupais=create_pais(["4m","5m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=4),fuloupais=create_pais(["2m","3m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=4),fuloupais=create_pais(["3m","5m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=4),fuloupais=create_pais(["5m","6m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=5),fuloupais=create_pais(["3m","4m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=5),fuloupais=create_pais(["4m","6m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=5),fuloupais=create_pais(["6m","7m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=6),fuloupais=create_pais(["4m","5m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=6),fuloupais=create_pais(["5m","7m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=6),fuloupais=create_pais(["7m","8m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=7),fuloupais=create_pais(["5m","6m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=7),fuloupais=create_pais(["6m","8m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=7),fuloupais=create_pais(["8m","9m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=8),fuloupais=create_pais(["6m","7m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=8),fuloupais=create_pais(["7m","9m"])) in fulou_candidates
    assert Fulou(type="chi",nakipai=Pai(suit="m",num=9),fuloupais=create_pais(["7m","8m"])) in fulou_candidates
    assert Fulou(type="peng",nakipai=Pai(suit="m",num=1),fuloupais=create_pais(["1m","1m"])) in fulou_candidates
    assert Fulou(type="minggang",nakipai=Pai(suit="m",num=1),fuloupais=create_pais(["1m","1m","1m"])) in fulou_candidates
    assert Fulou(type="peng",nakipai=Pai(suit="m",num=9),fuloupais=create_pais(["9m","9m"])) in fulou_candidates
    assert Fulou(type="minggang",nakipai=Pai(suit="m",num=9),fuloupais=create_pais(["9m","9m","9m"])) in fulou_candidates
    
    pais=[Pai.deserialize(s) for s in ["m5","m5","m5","m5t"]]
    fulou=[Fulou(type="peng",nakipai=Pai(suit="z",num=1),fuloupais=[Pai(suit="z",num=1),Pai(suit="z",num=1)],position="duimian")]
    zimopai=Pai.deserialize("z1")
    shoupai = Shoupai(bingpai=pais,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==4
    assert Fulou(type="peng",nakipai=Pai(suit="m",num=5),fuloupais=[Pai(suit="m",num=5),Pai(suit="m",num=5)]) in fulou_candidates
    assert Fulou(type="minggang",nakipai=Pai(suit="m",num=5),fuloupais=[Pai.deserialize(s) for s in ["m5","m5","m5"]]) in fulou_candidates
    assert Fulou(type="jiagang",nakipai=Pai(suit="z",num=1),fuloupais=[Pai.deserialize(s) for s in ["z1","z1"]]) in fulou_candidates
    assert Fulou(type="angang",fuloupais=[Pai.deserialize(s) for s in ["m5","m5","m5","m5"]]) in fulou_candidates
    
def test_compute_xiangting():
    pais = [Pai.deserialize(s) for s in 
            # ["m1",  "m1",  "p4",  "p4","p4","s3","s7"]
            # ["m1",  "m1",  "p4",  "p4","p4","s3","s4"]
            # ["m1",  "m9", "p1",  "p9",  "s1",  "s9",   "z1",  "z2","z3","z4","z5","z6","z7"]
            # ["m1",  "m1", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "m9", "m9"]
            ["m1",  "m1", "m2", "m2", "m3", "m3", "m4", "m4", "m5", "m5", "z5", "z6", "z7"]
    ]
    fulou=[Fulou.deserialize("angang,null,z1+z1+z1+z1,null"),Fulou.deserialize("angang,null,z2+z2+z2+z2,null")]
    shoupai = Shoupai(bingpai=pais,zimopai=Pai.deserialize("z6"))
    xiangting=shoupai._compute_xiangting()
    # print("hulecandidates",[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in shoupai.hule_candidates])
    print("xianting,shoupai.hule_candidates,zimopai,lizhi_candidates",xiangting,[ ("+".join([ x.serialize()[:2] for x in h.pais]),h.nums) for h in shoupai.hule_candidates],shoupai.zimopai.serialize()[:2],[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in shoupai.lizhi_candidates])
    # assert False
    
# def test_comupute_lizhi():
#     pais=[Pai.deserialize(s) for s in ["m1","m2","m4","m5"]]
#     shoupai = Shoupai(bingpai=pais)
#     xiangting=shoupai.compute_xiangting()


def test_fulou_serialize_and_deserialize():
    fulou=Fulou(type="peng")
    assert fulou.serialize()=="peng,null,null,null"
    fulou=Fulou(type="peng",nakipai=Pai(suit="m",num=3),fuloupais=[Pai.deserialize("m3"),Pai.deserialize("m3")],position="duimian")
    assert fulou.serialize()=="peng,m3f,m3f+m3f,duimian"
    fulou=Fulou(type="chi",nakipai=Pai(suit="m",num=1),fuloupais=[Pai.deserialize("m2"),Pai.deserialize("m3")],position="shangjia")
    assert fulou.serialize()=="chi,m1f,m2f+m3f,shangjia"
    fulou=Fulou(type="angang",fuloupais=[Pai.deserialize("z1") for _ in range(4)])
    assert fulou.serialize()=="angang,null,z1f+z1f+z1f+z1f,null"
    
    fulou=Fulou.deserialize("peng,null,null,null")
    assert fulou==Fulou(type="peng")
    fulou=Fulou.deserialize("peng,m3f,m3f+m3f,duimian")
    assert fulou==Fulou(type="peng",nakipai=Pai(suit="m",num=3),fuloupais=[Pai.deserialize("m3"),Pai.deserialize("m3")],position="duimian")
    fulou=Fulou.deserialize("chi,m1f,m2f+m3f,shangjia")
    assert fulou==Fulou(type="chi",nakipai=Pai(suit="m",num=1),fuloupais=[Pai.deserialize("m2"),Pai.deserialize("m3")],position="shangjia")
    fulou=Fulou.deserialize("angang,null,z1f+z1f+z1f+z1f,null")
    assert fulou==Fulou(type="angang",fuloupais=[Pai.deserialize("z1") for _ in range(4)])
 
def test_shoupai_init():
    shoupai=Shoupai()
    
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m2","m2","m3","m3","m4","m4","m5","m5","m6","m6","m7"]]
    shoupai=Shoupai(bingpai=bingpai)
    assert len(shoupai.bingpai)==13
    
    bingpai=[Pai.deserialize(s) for s in ["m1"]]
    fulou=[Fulou.deserialize(s) for s in ["chi,m1,m2+m3,shangjia","peng,z1,z1+z1,duimian","minggang,z2,z2+z2+z2,xiajia","angang,null,z3+z3+z3+z3,null"]]
    zimopai=Pai.deserialize("m2")
    shoupai=Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    assert len(shoupai.bingpai)==1
    assert len(shoupai.fulou)==4
    assert shoupai.zimopai==Pai.deserialize("m2")

def test_do_zimo():
    shoupai=Shoupai()
    for s in ["m1","m1","m2","m2","m3","m3","m4","m4","m5","m5","m6","m6","m7"]:
        shoupai.do_zimo(Pai.deserialize(s))
        shoupai.bingpai.append(shoupai.zimopai)
        shoupai.zimopai=None
    assert len(shoupai.bingpai)==13
    
    #例外
    shoupai=Shoupai()
    shoupai.do_zimo(Pai.deserialize("m1"))
    with pytest.raises(ValueError):
        assert shoupai.do_zimo(Pai.deserialize("m2"))
    
def test_do_dapai():
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m3","m3","m5","m5","m7","m7","m9","m9","z1","z1","z3"]]
    shoupai=Shoupai(bingpai=bingpai)
    #ツモ切り
    for s in ["m2","m2","m4","m4","m6","m6","m8","m8","z2","z2","z4","z4","z6"]:
        shoupai.zimopai=Pai.deserialize(s)
        shoupai.do_dapai(dapai=Pai.deserialize(s),dapai_idx=99)
    assert len(shoupai.bingpai)==13
    
    #手牌切り
    bingpai=[Pai.deserialize(s) for s in ["s1","s1","s3","s3","s5","s5","s7","s7","s9","s9","z1","z1","z3"]]
    shoupai=Shoupai(bingpai=bingpai)
    qawwse=0
    for s in ["m2","m2","m4","m4","m6","m6","m8","m8","p2","p2","p4","p4","p6"]:
        shoupai.zimopai=Pai.deserialize(s)
        shoupai.do_dapai(dapai=bingpai[qawwse],dapai_idx=qawwse)
        assert shoupai.bingpai[qawwse]==Pai.deserialize(s) #ソートされているか確認
        qawwse+=1
    assert len(shoupai.bingpai)==13
    
    #例外
    bingpai=[Pai.deserialize(s) for s in ["s1","s1","s3","s3","s5","s5","s7","s7","s9","s9","z1","z1","z3"]]
    shoupai=Shoupai(bingpai=bingpai)
    #牌番号と牌の不一致
    with pytest.raises(ValueError):
        shoupai.zimopai=Pai.deserialize("m1")
        shoupai.do_dapai(dapai=Pai.deserialize("m1"),dapai_idx=0)
    #リーチ中の手牌切り
    with pytest.raises(ValueError):
        shoupai.is_lizhi=True
        shoupai.zimopai=Pai.deserialize("m1")
        shoupai.do_dapai(dapai=Pai.deserialize("s1"),dapai_idx=0)
    #ツモ牌番号と牌の不一致
    with pytest.raises(ValueError):
        shoupai.zimopai=Pai.deserialize("m1")
        shoupai.do_dapai(dapai=Pai.deserialize("s1"),dapai_idx=99)
    #牌番号が範囲外
    with pytest.raises(ValueError):
        shoupai.zimopai=Pai.deserialize("m1")
        shoupai.do_dapai(dapai=Pai.deserialize("s1"),dapai_idx=14)

def test_do_fulou():
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","z1","z1","z2","z2","z2","z3","z3","z3","z3","z4","z4"]]
    fulou_candidates=[Fulou.deserialize(s) for s in ["chi,m1,m2+m3,null","peng,z1,z1+z1,null","jiagang,z1,z1+z1,null","minggang,z2,z2+z2+z2,null","angang,null,z3+z3+z3+z3,null"]]
    shoupai=Shoupai(bingpai=bingpai,fulou_candidates=fulou_candidates)
    
    #チー
    chi_shoupai=shoupai.model_copy(deep=True)
    fulou=Fulou.deserialize("chi,m1,m2+m3,shangjia")
    chi_shoupai.do_fulou(fulou)
    assert len(chi_shoupai.fulou)==1
    assert len(chi_shoupai.bingpai)==11
    assert chi_shoupai.fulou[0]==Fulou.deserialize("chi,m1,m2+m3,shangjia")
    chi_shoupai.bingpai.pop(-1)
    
    #ポン
    peng_shoupai=chi_shoupai.model_copy(deep=True)
    peng_shoupai.fulou_candidates=fulou_candidates
    fulou=Fulou.deserialize("peng,z1,z1+z1,duimian")
    peng_shoupai.do_fulou(fulou)
    assert len(peng_shoupai.fulou)==2
    assert len(peng_shoupai.bingpai)==8
    assert peng_shoupai.fulou[1]==Fulou.deserialize("peng,z1,z1+z1,duimian")
    peng_shoupai.bingpai.pop(-1)
    
    #明カン
    minggang_shoupai=peng_shoupai.model_copy(deep=True)
    minggang_shoupai.fulou_candidates=fulou_candidates
    fulou=Fulou.deserialize("minggang,z2,z2+z2+z2,xiajia")
    minggang_shoupai.do_fulou(fulou)
    assert len(minggang_shoupai.fulou)==3
    assert len(minggang_shoupai.bingpai)==4
    assert minggang_shoupai.fulou[2]==Fulou.deserialize("minggang,z2,z2+z2+z2,xiajia")
    
    #加槓 ツモ牌を追加
    jiagang_shoupai=minggang_shoupai.model_copy(deep=True)
    jiagang_shoupai.zimopai=Pai.deserialize("z1")
    jiagang_shoupai.fulou_candidates=fulou_candidates
    fulou=Fulou.deserialize("jiagang,z1,z1+z1,duimian")
    jiagang_shoupai.do_fulou(fulou)
    assert len(jiagang_shoupai.fulou)==3
    assert len(jiagang_shoupai.bingpai)==4
    assert Pai.deserialize("z1") not in jiagang_shoupai.bingpai
    assert jiagang_shoupai.zimopai==None
    assert jiagang_shoupai.fulou[1]==Fulou.deserialize("jiagang,z1,z1+z1+z1,duimian")
    
    #加槓 手牌を追加
    jiagang_shoupai=minggang_shoupai.model_copy(deep=True)
    bingpai=[Pai.deserialize(s) for s in ["z1","z2","z3","z4"]]
    jiagang_shoupai.bingpai=bingpai
    jiagang_shoupai.zimopai=Pai.deserialize("m1")
    jiagang_shoupai.fulou_candidates=fulou_candidates
    fulou=Fulou.deserialize("jiagang,z1,z1+z1,duimian")
    jiagang_shoupai.do_fulou(fulou)
    assert len(jiagang_shoupai.fulou)==3
    assert len(jiagang_shoupai.bingpai)==4
    assert Pai.deserialize("z1") not in jiagang_shoupai.bingpai
    assert jiagang_shoupai.zimopai==None
    assert jiagang_shoupai.fulou[1]==Fulou.deserialize("jiagang,z1,z1+z1+z1,duimian")
    
    #暗カン
    angang_shoupai=jiagang_shoupai.model_copy(deep=True)
    bingpai=[Pai.deserialize(s) for s in ["z3","z3","z3","z3"]]
    angang_shoupai.bingpai=bingpai
    angang_shoupai.fulou_candidates=fulou_candidates
    fulou=Fulou.deserialize("angang,null,z3+z3+z3+z3,null")
    angang_shoupai.do_fulou(fulou)
    assert len(angang_shoupai.fulou)==4
    assert len(angang_shoupai.bingpai)==0
    assert angang_shoupai.fulou[3]==Fulou.deserialize("angang,null,z3+z3+z3+z3,null")

def test_get_kokushi_xiangting():
    #国士13面待ち
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7"]]
    shoupai = Shoupai(bingpai=bingpai)
    xiangting_result = shoupai._get_kokushi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 13
    copy_bingpai=[p for p in bingpai]
    for pat in xiangting_result[2]:
        copy_bingpai.remove(pat.pais[-1])
    
    #国士単騎待ち
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7"]]
    for i,p in enumerate(bingpai):
        copy_bingpai=[p for p in bingpai]
        copy_bingpai[i]=bingpai[i-1]
        shoupai = Shoupai(bingpai=copy_bingpai)
        xiangting_result = shoupai._get_kokushi_xiangting()
        assert xiangting_result[0]==0
        assert len(xiangting_result[1]) == 1
        assert len(xiangting_result[2]) == 1
        assert xiangting_result[2][0].pais[-1] == bingpai[i]
        
    #国士シャンテン数確認
    yaojiupai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7"]]
    zhongzhangpai=[Pai.deserialize(s) for s in ["m2","m4","m6","m8","p2","p4","p6","p8","s2","s4","s6","s8","s5"]]
    for i in range(13):
        bingpai=zhongzhangpai[:i]+yaojiupai[i:]
        shoupai = Shoupai(bingpai=bingpai)
        xiangting_result = shoupai._get_kokushi_xiangting()
        assert xiangting_result[0]==i
        assert len(xiangting_result[1]) == 1
    
    #副露ありのシャン点数
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4"]]
    fulou=[Fulou.deserialize("peng,z5,z5+z5,duimian")]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_kokushi_xiangting()
    assert xiangting_result[0]==99
    assert len(xiangting_result[1]) == 0
    assert len(xiangting_result[2]) == 0
    
def test_get_qiduizi_xiangting():
    #七対子テンパイ
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","p1","p1","s1","s1","z1","z1","z3","z3","z5","z5","z7"]]
    shoupai = Shoupai(bingpai=bingpai)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 1
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("z7")
    
    #七対子シャン点数確認
    single_list=[Pai.deserialize(s) for s in ["p1","p2","p3","p4","p5","p6","p7","p8","p9","z1","z2","z3","z4"]]
    duizi_list=[Pai.deserialize(s) for s in ["m1","m1","m2","m2","m3","m3","m4","m4","m5","m5","m6","m6"]]
    for i in range(7):
        bingpai=duizi_list[:i*2]+single_list[i*2:]
        shoupai = Shoupai(bingpai=bingpai)
        xiangting_result = shoupai._get_qiduizi_xiangting()
        assert xiangting_result[0]==6-i
        assert len(xiangting_result[1]) == 1
    
    #副露ありのシャン点数
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4"]]
    fulou=[Fulou.deserialize("peng,z5,z5+z5,duimian")]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result[0]==99
    assert len(xiangting_result[1]) == 0
    assert len(xiangting_result[2]) == 0

def test_get_mianzi_xiangting():
    #単騎待ち
    bingpai=[Pai.deserialize(s) for s in ["m1"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia","angang,null,z4+z4+z4+z4,null"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 1
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    
    #3副露
    ##テンパイ:両面
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m3","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 2
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m5")
    
    ##テンパイ:ペンチャン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m8","m9"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 1
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m6","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 1
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 1
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:シャンポン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m7","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 1
    assert len(xiangting_result[2]) == 2
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:ノベタン
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 2
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m4")
    
    ##テンパイ:ペンチャン+単騎
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m2"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 2
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m3")
    
    ##テンパイ:カンチャン+単騎
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 2
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m3")
    
    ##テンパイ:両面+単騎
    bingpai=[Pai.deserialize(s) for s in ["m2","m2","m2","m3"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 3
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m4")
    
    ##イーシャンテン:雀頭あり
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m6","m9"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==1
    assert len(xiangting_result[1]) == 1
    assert xiangting_result[1][0].nums == [2,1,1]
    assert len(xiangting_result[2]) == 0
    
    ##イーシャンテン:雀頭なし
    bingpai=[Pai.deserialize(s) for s in ["m1","m3","m5","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==1
    assert len(xiangting_result[1]) == 1
    assert xiangting_result[1][0].nums == [2,2]
    assert len(xiangting_result[2]) == 0
    
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m5","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==1
    assert len(xiangting_result[1]) == 1
    assert xiangting_result[1][0].nums == [2,1,1]
    assert len(xiangting_result[2]) == 0
    
    #リャンシャンテン
    bingpai=[Pai.deserialize(s) for s in ["z1","z2","z3","z4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==2
    assert len(xiangting_result[1]) == 1
    assert xiangting_result[1][0].nums == [1,1,1,1]
    assert len(xiangting_result[2]) == 0
    
    #2副露
    ##テンパイ:両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m5","m6","z7","z7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 4
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+単騎+単騎
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m5","m6","m7","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 3
    assert len(xiangting_result[2]) == 3
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+単騎+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m5","m5","m6","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 3
    assert len(xiangting_result[2]) == 4
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:シャンポン+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m4","m4","m7","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 4
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m3","m3","m4","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 3
    assert len(xiangting_result[2]) == 5
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][4].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+両面+両面+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m4","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 4
    assert len(xiangting_result[2]) == 6
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][4].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][5].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+両面+カンチャン+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 4
    assert len(xiangting_result[2]) == 5
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][4].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+単騎+両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m6","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 4
    assert len(xiangting_result[2]) == 6
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result[2][2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result[2][4].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result[2][5].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m6","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result[0]==0
    assert len(xiangting_result[1]) == 2
    assert len(xiangting_result[2]) == 2
    assert xiangting_result[2][0].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result[2][1].pais[-1] == Pai.deserialize("m8")
    
    
    
    
    

    
    
    