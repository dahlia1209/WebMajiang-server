import pytest
from app.models.shoupai import Shoupai, Fulou
from app.models.pai import Pai


@pytest.fixture
def empty_shoupai():
    return Shoupai()


@pytest.fixture
def sample_shoupai():
    shoupai = Shoupai()
    pais = [
        Pai(id=1, suit="m", num=1),
        Pai(id=2, suit="m", num=2),
        Pai(id=3, suit="m", num=3),
        Pai(id=4, suit="p", num=4),
        Pai(id=5, suit="p", num=5),
        Pai(id=6, suit="p", num=6),
        Pai(id=7, suit="s", num=7),
        Pai(id=8, suit="s", num=8),
        Pai(id=9, suit="s", num=9),
        Pai(id=10, suit="z", num=1),
        Pai(id=11, suit="z", num=2),
        Pai(id=12, suit="z", num=3),
        Pai(id=13, suit="z", num=4),
    ]
    for pai in pais:
        shoupai.add_pai(pai)
    return shoupai


@pytest.fixture
def sample_shoupai_with_red_dora():
    shoupai = Shoupai()
    pais = [
        Pai(id=1, suit="m", num=2),
        Pai(id=2, suit="m", num=2),
        Pai(id=3, suit="m", num=3),
        Pai(id=4, suit="m", num=3),
        Pai(id=5, suit="m", num=4),
        Pai(id=6, suit="m", num=4),
        Pai(id=7, suit="m", num=5),
        Pai(id=8, suit="m", num=5, is_red=True),
        Pai(id=9, suit="m", num=6),
        Pai(id=10, suit="m", num=6),
        Pai(id=11, suit="m", num=7),
        Pai(id=12, suit="m", num=7),
        Pai(id=13, suit="m", num=7),
    ]
    for pai in pais:
        shoupai.add_pai(pai)
    return shoupai


@pytest.fixture
def sample_shoupai_for_peng_test():
    shoupai = Shoupai()
    pais = [
        Pai(id=1, suit="m", num=3),
        Pai(id=2, suit="m", num=3),
        Pai(id=3, suit="m", num=4),
        Pai(id=4, suit="m", num=4),
        Pai(id=5, suit="m", num=5),
        Pai(id=6, suit="m", num=5),
        Pai(id=7, suit="m", num=5, is_red=True),
        Pai(id=8, suit="m", num=6),
        Pai(id=9, suit="m", num=6),
        Pai(id=10, suit="m", num=6),
        Pai(id=11, suit="m", num=7),
        Pai(id=12, suit="m", num=7),
        Pai(id=13, suit="m", num=7),
    ]
    for pai in pais:
        shoupai.add_pai(pai)
    return shoupai


@pytest.fixture
def sample_shoupai_for_gang_test():
    shoupai = Shoupai()
    pais = [
        Pai(id=1, suit="m", num=3),
        Pai(id=2, suit="m", num=3),
        Pai(id=3, suit="m", num=3),
        Pai(id=4, suit="m", num=3),
        Pai(id=5, suit="m", num=5),
        Pai(id=6, suit="m", num=5),
        Pai(id=7, suit="m", num=5, is_red=True),
        Pai(id=8, suit="z", num=6),
        Pai(id=9, suit="z", num=6),
        Pai(id=10, suit="z", num=6),
        Pai(id=11, suit="m", num=6),
        Pai(id=12, suit="m", num=7),
        Pai(id=13, suit="m", num=7),
    ]
    for pai in pais:
        shoupai.add_pai(pai)
    return shoupai


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
    shoupai.compute_fulou_candidates()
    fulou=Fulou.deserialize("chi,m1f,m2f+m3f,shangjia")
    shoupai.do_fulou(fulou)
    assert len(shoupai.fulou) == 1

def test_do_peng():
    # 1回目のポン
    pais = create_pais(
        ["1m", "1m", "1m", "3m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai.compute_fulou_candidates()
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
    shoupai.compute_fulou_candidates()
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
    shoupai.compute_fulou_candidates()
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
    shoupai.compute_fulou_candidates()
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
    shoupai.compute_fulou_candidates()
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
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=7) 


def test_qidui_not_tenpai():
    # 七対子非テンパイ: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 7s 8m
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "7s", "8m"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0


def test_kokushi_tenpai():
    # 国士無双テンパイ: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 7z
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 13
    # assert shoupai.hule_candidates[0]==Pai(suit="m", num=7) 



def test_kokushi_not_tenpai():
    # 国士無双非テンパイ: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 8s
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "8s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
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
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==2
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=1, suit="m")
    assert shoupai.hule_candidates[1].pais[-1] == Pai(num=1, suit="z")
    
    # mianzi_pai = Shoupai.get_mianzi_pai(pais)
    # assert len(mianzi_pai) == 1
    # assert mianzi_pai[0] == Pai(num=1, suit="m")

    # 2
    pais = create_pais(["1m", "2m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==1
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=3, suit="m")

    # 3
    pais = create_pais(["8m", "9m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==1
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=7, suit="m")
    
    # 4
    pais = create_pais(["7m", "9m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==1
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=8, suit="m")
    
    # 5
    pais = create_pais(["7m", "8m","1z","1z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==2
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=6, suit="m")
    assert shoupai.hule_candidates[1].pais[-1] == Pai(num=9, suit="m")
    
    # 6
    pais = create_pais(["1z", "1z","2z", "2z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==2
    assert shoupai.hule_candidates[0].pais[-1] == Pai(num=1, suit="z")
    assert shoupai.hule_candidates[1].pais[-1] == Pai(num=2, suit="z")

    # 7
    pais = create_pais(["1z", "2z","3z", "3z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==0


    # 8
    pais = create_pais(["1m", "4m","3z", "3z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==0
    
    # 9
    pais = create_pais(["5m", "6z","3z", "3z"])
    shoupai=Shoupai(bingpai=pais)
    shoupai.compute_xiangting()
    assert len(shoupai.hule_candidates)==0

def test_find_agari_hai():
    # アガリ牌の抽出
    # 1
    pais = create_pais(["1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)

    # 2
    pais = create_pais(["1m", "1m", "3m", "4m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=5)

    # 3
    pais = create_pais(["1m", "1m", "3m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=4)

    # 4
    pais = create_pais(["1m", "1m", "8m", "9m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=7)

    # 5
    pais = create_pais(["1m", "1m", "2m", "2m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=2)

    # 6
    pais = create_pais(["1m", "3m", "4m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=5)

    # 7
    pais = create_pais(["1m", "3m", "5m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=4)

    # 8
    pais = create_pais(["1m", "8m", "9m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=7)

    # 9
    pais = create_pais(["1m", "2m", "2m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="m", num=2)
    
    # 11
    pais = create_pais(["1z", "1z", "1m", "1m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="m", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="z", num=1)

    # 12
    pais = create_pais(["1z", "2z", "3m", "3m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0

    # 13
    pais = create_pais(["2z", "2z", "3m", "6m"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==1
    assert len(shoupai.hule_candidates) == 0

    # 14
    pais = create_pais(["1s", "2s", "3s", "6s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=6)

    # 15
    pais = create_pais(["1s", "3s", "6z", "2s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="z", num=6)

    # 16
    pais = create_pais(["1s", "2s", "3s", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    # print("xianting,best_combi",xiangting,[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in shoupai.hule_candidates])
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=4)

    # 17
    pais = create_pais(["1s", "2s", "2s", "2s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)

    # 18
    pais = create_pais(["3s", "2s", "2s", "2s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="s", num=4)

    # 19
    pais = create_pais(["3z", "2z", "2z", "2z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="z", num=3)

    # 20
    pais = create_pais(["2z", "2z", "2z", "2z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    # assert xiangting==1

    # 21
    pais = create_pais(["1s", "2s", "3s", "3s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)

    # 22
    pais = create_pais(["3s", "2s", "4s", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="s", num=4)


    # 23
    pais = create_pais(["4s", "2s", "4s", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="s", num=3)

    # 24
    pais = create_pais(["4s", "2s", "4p", "4s"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==1

    # 25
    pais = create_pais(["1p", "2p", "3p", "6p", "7p", "9p", "9p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=8)

    # 多面帳1
    pais = create_pais(["2p", "3p", "4p", "5p", "6p", "1z", "1z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=7)

    # 多面帳2
    pais = create_pais(["2p", "3p", "4p", "5p", "6p", "7p", "8p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=8)

    # 多面帳3
    pais = create_pais(["2p", "3p", "4p", "5p", "5p", "6p", "7p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=2)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=8)
    # 多面帳4
    pais = create_pais(["2p", "3p", "4p", "4p", "4p", "1z", "1z"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=1)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="z", num=1)

    # 多面帳5
    pais = create_pais(["2p", "3p", "3p", "3p", "4p", "5p", "6p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 2
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=7)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=8)

    # 多面帳10
    pais = create_pais(["3p", "3p", "3p", "5p", "5p", "6p", "7p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=8)

    # 多面帳11
    pais = create_pais(["3p", "3p", "3p", "5p", "6p", "7p", "8p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=8)

    # 多面帳12
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) == 4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=5)

    # 多面帳14
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==3
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=5)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=6)

    # 多面帳17
    pais = create_pais(["3p", "3p", "4p", "5p", "5p", "5p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==4
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[1].pais[-1]==Pai(suit="p", num=3)
    assert shoupai.hule_candidates[2].pais[-1]==Pai(suit="p", num=4)
    assert shoupai.hule_candidates[3].pais[-1]==Pai(suit="p", num=6)

    # 多面帳18
    pais = create_pais(["3p", "3p", "4p", "4p", "4p", "4p", "5p"])
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
    
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
    xiangting = shoupai.compute_xiangting()
    
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
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    fulou_candidates=shoupai.compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 24

    # 2
    pais = create_pais(["1m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai.compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 0
    # 3
    pais = create_pais(["1m", "2m", "5m", "9m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai.compute_fulou_candidates()
    assert len(shoupai.fulou_candidates) == 1
    # 4
    pais = create_pais(["1m", "2m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
    assert xiangting==0
    assert len(shoupai.hule_candidates) ==1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=2)

def test_regular_tenpai_penchan():
    # 辺張待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "1p", "1p", "1p", "1s", "1s", "8s", "9s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting == 0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="s", num=7)


def test_regular_tenpai_tanki():
    # 4面子1雀頭テンパイ（単騎待ち）
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1p", "1s"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
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
    xiangting = shoupai.compute_xiangting()
    assert xiangting==6
    assert len(shoupai.hule_candidates) ==0

def test_chiitoitsu_tenpai():
    # 七対子テンパイ（チートイツ）: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 6s 7z
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "6s", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting = shoupai.compute_xiangting()
    assert xiangting == 0
    assert len(shoupai.hule_candidates) == 1
    assert shoupai.hule_candidates[0].pais[-1]==Pai(suit="z", num=7) 

def test_kokushi_13_way_tenpai():
    # 国士無双13面待ち: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 7z
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    xiangting=shoupai.compute_xiangting()
    assert xiangting == 0
    assert len(shoupai.hule_candidates) == 13

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
    
def test_compute_fulou_candidates_2():
    pais = create_pais(
        ["1m", "1m", "1m", "2m","3m","4m","5m","6m","7m","8m","9m","9m","9m"]
    )
    shoupai = Shoupai(bingpai=pais)
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    shoupai = Shoupai(bingpai=pais,fulou=fulou)
    fulou_candidates=shoupai.compute_fulou_candidates()
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
    xiangting=shoupai.compute_xiangting()
    # print("hulecandidates",[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in shoupai.hule_candidates])
    print("xianting,shoupai.hule_candidates,zimopai,lizhi_candidates",xiangting,[ ("+".join([ x.serialize()[:2] for x in h.pais]),h.nums) for h in shoupai.hule_candidates],shoupai.zimopai.serialize()[:2],[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in shoupai.lizhi_candidates])
    assert False
    
# def test_comupute_lizhi():
#     pais=[Pai.deserialize(s) for s in ["m1","m2","m4","m5"]]
#     shoupai = Shoupai(bingpai=pais)
#     xiangting=shoupai.compute_xiangting()
    