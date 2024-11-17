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


def test_set_zimo():
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2p", "3p"]
    )
    shoupai=Shoupai(bingpai=pais)
    zimopai=Pai(suit='m',num=1)
    shoupai.zimopai=None
    shoupai.set_zimopai(zimopai)
    assert shoupai.zimopai == Pai(suit="m", num=1)
    shoupai.remove_pai_from_zimopai()
    assert shoupai.zimopai == None

def test_sort_pai():
    pais = [
        Pai(suit="z", num=1),
        Pai(suit="m", num=8),
        Pai(suit="m", num=2),
        Pai(suit="p", num=2),
        Pai(suit="s", num=6),
    ]
    sort_pai = Shoupai.sort_pai(pais)
    assert sort_pai[0] == Pai(suit="m", num=2)
    assert sort_pai[1] == Pai(suit="m", num=8)
    assert sort_pai[2] == Pai(suit="p", num=2)
    assert sort_pai[3] == Pai(suit="s", num=6)
    assert sort_pai[4] == Pai(suit="z", num=1)


def test_remove_pai():
    pais = create_pais(["1m", "2m", "3m", "4m", "5m", "5m"])
    zimopai = Pai(num=5, suit="m")
    shoupai = Shoupai(bingpai=pais, zimopai=zimopai)
    shoupai.remove_pai_from_zimopai()
    assert shoupai.zimopai == None
    assert len(shoupai.bingpai) == 6

    shoupai.zimopai = Pai(num=5, suit="m")
    shoupai.remove_pai_from_bingpai(index=3)
    assert shoupai.zimopai == Pai(num=5, suit="m")
    assert len(shoupai.bingpai) == 5
    shoupai.zimo_into_bingpai()
    assert len(shoupai.bingpai) == 6
    assert shoupai.zimopai == None


def test_do_chi():
    # 1回目のチー
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    nakipai = Pai(suit="m", num=1)
    fulou_pai = shoupai.get_fulou_pai(nakipai)
    shoupai.do_fulou(fulou_pai[0])
    assert len(shoupai.fulou) == 1

# def test_fulou_koho():
#     # 1回目のチー
#     pais = create_pais(
#         ["1m", "1m","1m","2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "9m", "9m"]
#     )
#     shoupai = Shoupai(bingpai=pais)
#     shoupai.set_fulou_pai_from_shoupai()
#     [print(f.model_dump_json()) for f in shoupai.waiting_fulou_pai]
#     assert 2 == 1


def test_do_peng(sample_shoupai_for_peng_test):
    # 1回目のポン
    pais = create_pais(
        ["1m", "1m", "1m", "3m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    nakipai = Pai(suit="m", num=3)
    fulou_pai = shoupai.get_fulou_pai(nakipai)
    shoupai.do_fulou(fulou_pai[0])
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="peng",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=3, suit="m"),
            Pai(num=3, suit="m"),
        ],
    )

def test_do_minggang(sample_shoupai_for_gang_test):
    # カン1回目
    pais = create_pais(
        ["1m", "1m", "1m", "3m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    nakipai = Pai(suit="m", num=1)
    fulou_pai = shoupai.get_fulou_pai(nakipai)
    shoupai.do_fulou(fulou_pai[1])
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="minggang",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
        ],
    )

def test_get_main_fulou_pai():
    # 暗槓
    pais = create_pais(
        ["1m", "1m", "1m", "1m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais, zimopai=Pai(suit="m", num=5))
    main_fulou_pai = shoupai.get_main_fulou_pai()
    assert len(main_fulou_pai) == 2
    assert main_fulou_pai[0] == Fulou(
        type="angang",
        nakipai=None,
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
        ],
    )
    assert main_fulou_pai[1] == Fulou(
        type="angang",
        nakipai=None,
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )
    # 加槓
    pais = create_pais(["1m", "1m", "1m", "1m", "3m", "1p", "1p", "1p", "2p", "3p"])
    nakipai = Pai(num=5, suit="m")
    fuloupais = create_pais(["5m", "5m"])
    fulou = Fulou(type="peng", nakipai=nakipai, fuloupais=fuloupais)
    shoupai = Shoupai(
        bingpai=pais, zimopai=Pai(suit="m", num=5, is_red=True), fulou=[fulou]
    )
    main_fulou_pai = shoupai.get_main_fulou_pai()
    assert len(main_fulou_pai) == 2
    assert main_fulou_pai[0] == Fulou(
        type="angang",
        nakipai=None,
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
        ],
    )
    assert main_fulou_pai[1] == Fulou(
        type="jiagang",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m", is_red=True),
        ],
    )


def test_do_angang():
    # 暗槓1回目
    pais = create_pais(
        ["1m", "1m", "1m", "1m", "3m", "5m", "5m", "5m", "1p", "1p", "1p", "2p", "3p"]
    )
    shoupai = Shoupai(bingpai=pais, zimopai=Pai(suit="m", num=5, is_red=True))
    main_fulou_pai = shoupai.get_main_fulou_pai()
    shoupai.do_fulou(main_fulou_pai[1])
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="angang",
        nakipai=None,
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m", is_red=True),
        ],
    )
    assert shoupai.zimopai == None
    assert len(shoupai.bingpai) == 10
    assert shoupai.bingpai == create_pais(
        ["1m", "1m", "1m", "1m", "3m", "1p", "1p", "1p", "2p", "3p"]
    )

    # 暗槓２回目
    shoupai.zimopai = Pai(suit="p", num=1)
    main_fulou_pai = shoupai.get_main_fulou_pai()
    shoupai.do_fulou(main_fulou_pai[1])
    assert len(shoupai.fulou) == 2
    assert shoupai.fulou[1] == Fulou(
        type="angang",
        nakipai=None,
        fuloupais=[
            Pai(num=1, suit="p"),
            Pai(num=1, suit="p"),
            Pai(num=1, suit="p"),
            Pai(num=1, suit="p"),
        ],
    )


@pytest.fixture
def sample_shoupai_for_jiagang_test():
    shoupai = Shoupai()
    pais = [
        Pai(id=1, suit="m", num=3),
        Pai(id=2, suit="m", num=3),
        Pai(id=3, suit="m", num=3),
        Pai(id=4, suit="m", num=4),
        Pai(id=5, suit="m", num=4),
        Pai(id=6, suit="m", num=5),
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

    # Add a peng to fulou
    nakipai = Pai(id=14, suit="m", num=6)
    fuloupais = (Pai(id=9, suit="m", num=6), Pai(id=10, suit="m", num=6))
    shoupai.do_fulou("peng", nakipai, fuloupais)

    return shoupai


def test_do_jiagang():
    # 加槓1回目
    pais = create_pais(["1m", "1m", "1m", "1m", "3m", "1p", "1p", "1p", "2p", "3p"])
    fulou = Fulou(
        type="peng", nakipai=Pai(num=5, suit="m"), fuloupais=create_pais(["5m", "5m"])
    )
    zimopai = Pai(num=5, suit="m", is_red=True)
    shoupai = Shoupai(bingpai=pais, zimopai=zimopai, fulou=[fulou])
    main_fulou_pai = shoupai.get_main_fulou_pai()
    assert main_fulou_pai[1] == Fulou(
        type="jiagang", nakipai=Pai(num=5, suit="m"), fuloupais=(create_pais(["5m", "5m"])+[zimopai])
    )
    assert main_fulou_pai[1].fuloupais[-1]==zimopai
    shoupai.do_fulou(main_fulou_pai[1])
    assert len(shoupai.fulou) == 1
    assert shoupai.fulou[0] == Fulou(
        type="jiagang",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m", is_red=True),
        ],
    )


def create_pais(pai_strings):
    return [Pai(suit=s[1], num=int(s[0])) for i, s in enumerate(pai_strings)]


def test_qidui_tenpai():
    # 七対子テンパイ: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 6s 7m
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "6s", "7m"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 1
    assert Pai(suit="m", num=7) in agari_pais


def test_qidui_not_tenpai():
    # 七対子非テンパイ: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 7s 8m
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "7s", "8m"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == False
    assert len(agari_pais) == 0


def test_kokushi_tenpai():
    # 国士無双テンパイ: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 7z
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 13  # 13枚の幺九牌全てが和了牌


def test_kokushi_not_tenpai():
    # 国士無双非テンパイ: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 8s
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "8s"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == False
    assert len(agari_pais) == 0


def test_is_shuntsu():
    # 順子
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="m", num=1, is_red=False),
            Pai(suit="m", num=2, is_red=False),
            Pai(suit="m", num=3, is_red=False),
        ]
    )
    assert is_shuntsu == True
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="m", num=1, is_red=False),
            Pai(suit="m", num=2, is_red=False),
            Pai(suit="m", num=4, is_red=False),
        ]
    )
    assert is_shuntsu == False
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="m", num=2, is_red=False),
            Pai(suit="m", num=3, is_red=False),
            Pai(suit="m", num=1, is_red=False),
        ]
    )
    assert is_shuntsu == True
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="s", num=1, is_red=False),
            Pai(suit="m", num=2, is_red=False),
            Pai(suit="m", num=3, is_red=False),
        ]
    )
    assert is_shuntsu == False
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="p", num=1, is_red=False),
            Pai(suit="p", num=2, is_red=False),
            Pai(suit="p", num=3, is_red=False),
        ]
    )
    assert is_shuntsu == True
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="z", num=1, is_red=False),
            Pai(suit="z", num=2, is_red=False),
            Pai(suit="z", num=3, is_red=False),
        ]
    )
    assert is_shuntsu == False
    is_shuntsu = Shoupai.is_shunzi(
        [
            Pai(suit="z", num=1, is_red=False),
            Pai(suit="z", num=1, is_red=False),
            Pai(suit="z", num=1, is_red=False),
        ]
    )
    assert is_shuntsu == False
    is_kezi = Shoupai.is_shunzi([Pai(suit="m", num=1, is_red=False)])
    assert is_kezi == False


def test_is_kezi():
    # 刻子
    is_kezi = Shoupai.is_kezi(
        [
            Pai(suit="m", num=1, is_red=False),
            Pai(suit="m", num=1, is_red=False),
            Pai(suit="m", num=1, is_red=False),
        ]
    )
    assert is_kezi == True
    is_kezi = Shoupai.is_kezi(
        [
            Pai(suit="m", num=1, is_red=False),
            Pai(suit="m", num=2, is_red=False),
            Pai(suit="m", num=3, is_red=False),
        ]
    )
    assert is_kezi == False
    is_kezi = Shoupai.is_kezi(
        [
            Pai(suit="p", num=9, is_red=False),
            Pai(suit="p", num=9, is_red=False),
            Pai(suit="p", num=9, is_red=False),
        ]
    )
    assert is_kezi == True
    is_kezi = Shoupai.is_kezi(
        [
            Pai(suit="m", num=9, is_red=False),
            Pai(suit="p", num=9, is_red=False),
            Pai(suit="p", num=9, is_red=False),
        ]
    )
    assert is_kezi == False
    is_kezi = Shoupai.is_kezi(
        [
            Pai(suit="s", num=9, is_red=False),
            Pai(suit="s", num=9, is_red=False),
            Pai(suit="s", num=9, is_red=False),
        ]
    )
    assert is_kezi == True
    is_kezi = Shoupai.is_kezi(
        [
            Pai(suit="z", num=7, is_red=False),
            Pai(suit="z", num=7, is_red=False),
            Pai(suit="z", num=7, is_red=False),
        ]
    )
    assert is_kezi == True
    is_kezi = Shoupai.is_kezi([Pai(suit="m", num=1, is_red=False)])
    assert is_kezi == False


def test_is_dazi():
    # 搭子
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="m", num=1, is_red=False), Pai(suit="m", num=2, is_red=False)]
    )
    assert is_dazi == True
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="m", num=1, is_red=False), Pai(suit="m", num=3, is_red=False)]
    )
    assert is_dazi == True
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="m", num=2, is_red=False), Pai(suit="m", num=3, is_red=False)]
    )
    assert is_dazi == True
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="m", num=9, is_red=False), Pai(suit="m", num=7, is_red=False)]
    )
    assert is_dazi == True
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="s", num=9, is_red=False), Pai(suit="s", num=7, is_red=False)]
    )
    assert is_dazi == True
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="p", num=9, is_red=False), Pai(suit="p", num=7, is_red=False)]
    )
    assert is_dazi == True
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="z", num=7, is_red=False), Pai(suit="z", num=5, is_red=False)]
    )
    assert is_dazi == False
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="p", num=7, is_red=False), Pai(suit="p", num=7, is_red=False)]
    )
    assert is_dazi == False
    is_dazi = Shoupai.is_dazi(
        [Pai(suit="p", num=7, is_red=False), Pai(suit="s", num=6, is_red=False)]
    )
    assert is_dazi == False
    is_dazi = Shoupai.is_dazi([Pai(suit="p", num=7, is_red=False)])
    assert is_dazi == False


def test_is_duizi():
    # 搭子
    is_duizi = Shoupai.is_duizi(
        [Pai(suit="m", num=1, is_red=False), Pai(suit="m", num=1, is_red=False)]
    )
    assert is_duizi == True
    is_duizi = Shoupai.is_duizi(
        [Pai(suit="m", num=5, is_red=False), Pai(suit="m", num=5, is_red=True)]
    )
    assert is_duizi == True
    is_duizi = Shoupai.is_duizi(
        [Pai(suit="s", num=5, is_red=False), Pai(suit="s", num=5, is_red=False)]
    )
    assert is_duizi == True
    is_duizi = Shoupai.is_duizi(
        [Pai(suit="s", num=5, is_red=False), Pai(suit="s", num=6, is_red=False)]
    )
    assert is_duizi == False


def test_is_gangzi():
    # 槓子
    # 1
    pais = create_pais(["1m", "1m", "1m", "1m"])
    is_gangzi = Shoupai.is_gangzi(pais)
    assert is_gangzi == True
    # 2
    pais = create_pais(["1p", "1p", "1p", "1p"])
    is_gangzi = Shoupai.is_gangzi(pais)
    assert is_gangzi == True
    # 3
    pais = create_pais(["1z", "1z", "1z", "1z"])
    is_gangzi = Shoupai.is_gangzi(pais)
    assert is_gangzi == True
    # 4
    pais = create_pais(["1z", "1z", "1z", "2z"])
    is_gangzi = Shoupai.is_gangzi(pais)
    assert is_gangzi == False


def test_remove_duplicates():
    # 牌の重複削除
    # 1
    pais = create_pais(
        ["1m", "1m", "2m", "2m", "3m", "3m", "4m", "4m", "5m", "5m", "6m", "6m", "7m"]
    )
    remove_duplicates = Shoupai.remove_duplicates(pais)
    assert len(remove_duplicates) == 7

    # 2
    pais = create_pais(
        ["1m", "1m", "1m", "1m", "2m", "2m", "2m", "3m", "4m", "4m", "5m", "5m", "5m"]
    )
    remove_duplicates = Shoupai.remove_duplicates(pais)
    assert len(remove_duplicates) == 5

    # 3
    pais = create_pais(
        ["1m", "1p", "1s", "1z", "2m", "2p", "2s", "2z", "3m", "3p", "3z", "3s", "4m"]
    )
    remove_duplicates = Shoupai.remove_duplicates(pais)
    assert len(remove_duplicates) == 13

    # 4
    pais = create_pais(
        ["1m", "1m", "1z", "1z", "2s", "2s", "2p", "2p", "3m", "3m", "3m", "3m", "5m"]
    )
    remove_duplicates = Shoupai.remove_duplicates(pais)
    assert len(remove_duplicates) == 6


def test_get_mianzi_pai():
    # 1
    pais = create_pais(["1m", "1m"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 1
    assert mianzi_pai[0] == Pai(num=1, suit="m")

    # 2
    pais = create_pais(["1m", "2m"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 1
    assert mianzi_pai[0] == Pai(num=3, suit="m")

    # 3
    pais = create_pais(["8m", "9m"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 1
    assert mianzi_pai[0] == Pai(num=7, suit="m")

    # 4
    pais = create_pais(["7m", "9m"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 1
    assert mianzi_pai[0] == Pai(num=8, suit="m")

    # 5
    pais = create_pais(["7m", "8m"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 2
    assert mianzi_pai[0] == Pai(num=6, suit="m")
    assert mianzi_pai[1] == Pai(num=9, suit="m")

    # 6
    pais = create_pais(["1z", "1z"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 1
    assert mianzi_pai[0] == Pai(num=1, suit="z")

    # 7
    pais = create_pais(["1z", "2z"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 0

    # 8
    pais = create_pais(["1m", "4m"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 0

    # 9
    pais = create_pais(["5m", "6z"])
    mianzi_pai = Shoupai.get_mianzi_pai(pais)
    assert len(mianzi_pai) == 0


def test_find_agari_hai():
    # アガリ牌の抽出
    # 1
    pais = create_pais(["1m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=1, suit="m")

    # 2
    pais = create_pais(["1m", "1m", "3m", "4m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=2, suit="m")
    assert agari_hai[1] == Pai(num=5, suit="m")

    # 3
    pais = create_pais(["1m", "1m", "3m", "5m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=4, suit="m")

    # 4
    pais = create_pais(["1m", "1m", "8m", "9m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=7, suit="m")

    # 5
    pais = create_pais(["1m", "1m", "2m", "2m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=1, suit="m")
    assert agari_hai[1] == Pai(num=2, suit="m")

    # 6
    pais = create_pais(["1m", "3m", "4m", "1m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=2, suit="m")
    assert agari_hai[1] == Pai(num=5, suit="m")

    # 7
    pais = create_pais(["1m", "3m", "5m", "1m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=4, suit="m")

    # 8
    pais = create_pais(["1m", "8m", "9m", "1m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=7, suit="m")

    # 9
    pais = create_pais(["1m", "2m", "2m", "1m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=1, suit="m")
    assert agari_hai[1] == Pai(num=2, suit="m")

    # 10
    pais = create_pais(["1z", "1z", "1m", "1m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=1, suit="m")
    assert agari_hai[1] == Pai(num=1, suit="z")

    # 10
    pais = create_pais(["1z", "2z", "3m", "3m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 0

    # 11
    pais = create_pais(["2z", "2z", "3m", "6m"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 0

    # 12
    pais = create_pais(["1s", "2s", "3s", "6s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=6, suit="s")

    # 13
    pais = create_pais(["1s", "2s", "3s", "6s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=6, suit="s")

    # 14
    pais = create_pais(["1s", "3s", "6s", "2s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=6, suit="s")

    # 15
    pais = create_pais(["1s", "3s", "6z", "2s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=6, suit="z")

    # 16
    pais = create_pais(["1s", "2s", "3s", "4s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=1, suit="s")
    assert agari_hai[1] == Pai(num=4, suit="s")

    # 17
    pais = create_pais(["1s", "2s", "2s", "2s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=1, suit="s")
    assert agari_hai[1] == Pai(num=3, suit="s")

    # 18
    pais = create_pais(["3s", "2s", "2s", "2s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=1, suit="s")
    assert agari_hai[1] == Pai(num=3, suit="s")
    assert agari_hai[2] == Pai(num=4, suit="s")

    # 19
    pais = create_pais(["3z", "2z", "2z", "2z"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=3, suit="z")

    # 20
    pais = create_pais(["2z", "2z", "2z", "2z"])
    agari_hai = Shoupai.get_agari_pai(pais)
    assert len(agari_hai) == 0

    # 21
    pais = create_pais(["1s", "2s", "3s", "3s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 1
    assert agari_hai[0] == Pai(num=3, suit="s")

    # 22
    pais = create_pais(["3s", "2s", "4s", "4s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=1, suit="s")
    assert agari_hai[1] == Pai(num=4, suit="s")

    # 23
    pais = create_pais(["4s", "2s", "4s", "4s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=2, suit="s")
    assert agari_hai[1] == Pai(num=3, suit="s")

    # 24
    pais = create_pais(["4s", "2s", "4p", "4s"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 0

    # 25
    pais = create_pais(["1p", "2p", "3p", "6p", "7p", "9p", "9p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=5, suit="p")
    assert agari_hai[1] == Pai(num=8, suit="p")

    # 多面帳1
    pais = create_pais(["2p", "3p", "4p", "5p", "6p", "1z", "1z"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=1, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=7, suit="p")

    # 多面帳2
    pais = create_pais(["2p", "3p", "4p", "5p", "6p", "7p", "8p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=5, suit="p")
    assert agari_hai[2] == Pai(num=8, suit="p")

    # 多面帳3
    pais = create_pais(["2p", "3p", "4p", "5p", "5p", "6p", "7p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=5, suit="p")
    assert agari_hai[2] == Pai(num=8, suit="p")

    # 多面帳4
    pais = create_pais(["2p", "3p", "4p", "4p", "4p", "1z", "1z"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=1, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=1, suit="z")

    # 多面帳5
    pais = create_pais(["2p", "3p", "3p", "3p", "4p", "5p", "6p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=1, suit="p")
    assert agari_hai[1] == Pai(num=2, suit="p")
    assert agari_hai[2] == Pai(num=4, suit="p")
    assert agari_hai[3] == Pai(num=7, suit="p")

    # 多面帳6
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "5p", "6p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=7, suit="p")

    # 多面帳7
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "5p", "6p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=4, suit="p")
    assert agari_hai[1] == Pai(num=5, suit="p")
    assert agari_hai[2] == Pai(num=7, suit="p")

    # 多面帳8
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "6p", "7p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 5
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=7, suit="p")
    assert agari_hai[4] == Pai(num=8, suit="p")

    # 多面帳9
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "6p", "8p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 2
    assert agari_hai[0] == Pai(num=7, suit="p")
    assert agari_hai[1] == Pai(num=8, suit="p")

    # 多面帳10
    pais = create_pais(["3p", "3p", "3p", "5p", "5p", "6p", "7p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=4, suit="p")
    assert agari_hai[1] == Pai(num=5, suit="p")
    assert agari_hai[2] == Pai(num=8, suit="p")

    # 多面帳11
    pais = create_pais(["3p", "3p", "3p", "5p", "6p", "7p", "8p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=4, suit="p")
    assert agari_hai[1] == Pai(num=5, suit="p")
    assert agari_hai[2] == Pai(num=8, suit="p")

    # 多面帳12
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "5p", "5p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=3, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=6, suit="p")

    # 多面帳13
    pais = create_pais(["3p", "3p", "4p", "4p", "4p", "5p", "5p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=3, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")

    # 多面帳14
    pais = create_pais(["3p", "3p", "3p", "4p", "5p", "5p", "5p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 5
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=3, suit="p")
    assert agari_hai[2] == Pai(num=4, suit="p")
    assert agari_hai[3] == Pai(num=5, suit="p")
    assert agari_hai[4] == Pai(num=6, suit="p")

    # 多面帳15
    pais = create_pais(["3p", "3p", "3p", "4p", "4p", "4p", "5p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=3, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=6, suit="p")

    # 多面帳16
    pais = create_pais(["3p", "3p", "3p", "5p", "7p", "7p", "7p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=4, suit="p")
    assert agari_hai[1] == Pai(num=5, suit="p")
    assert agari_hai[2] == Pai(num=6, suit="p")

    # 多面帳17
    pais = create_pais(["3p", "3p", "4p", "5p", "5p", "5p", "5p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 3
    assert agari_hai[0] == Pai(num=3, suit="p")
    assert agari_hai[1] == Pai(num=4, suit="p")
    assert agari_hai[2] == Pai(num=6, suit="p")

    # 多面帳18
    pais = create_pais(["3p", "3p", "4p", "4p", "4p", "4p", "5p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=3, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=6, suit="p")

    # 多面帳19
    pais = create_pais(["3p", "4p", "4p", "4p", "4p", "5p", "6p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=3, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=6, suit="p")

    # 多面帳Ex
    pais = create_pais(["4p", "4p", "4p", "3p", "4p", "5p", "6p"])
    agari_hai = Shoupai.get_agari_pai(pais)
    print("agari_hai", agari_hai)
    assert len(agari_hai) == 4
    assert agari_hai[0] == Pai(num=2, suit="p")
    assert agari_hai[1] == Pai(num=3, suit="p")
    assert agari_hai[2] == Pai(num=5, suit="p")
    assert agari_hai[3] == Pai(num=6, suit="p")


def test_get_fulou_pai_from_shoupai():
    # 副露牌候補セット
    # 1
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    fulou_pai = shoupai.get_fulou_pai(Pai(num=3, suit="m"))
    assert len(fulou_pai) == 3
    assert fulou_pai[0] == Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=2, suit="m"),
        ],
    )
    assert fulou_pai[1] == Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=2, suit="m"),
            Pai(num=4, suit="m"),
        ],
    )
    assert fulou_pai[2] == Fulou(
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
    shoupai.set_fulou_pai_from_shoupai()
    fulou_pai = shoupai.get_fulou_pai(Pai(num=1, suit="m"))
    assert len(fulou_pai) == 3
    assert fulou_pai[0] == Fulou(
        type="chi",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[
            Pai(num=2, suit="m"),
            Pai(num=3, suit="m"),
        ],
    )
    assert fulou_pai[1] == Fulou(
        type="peng",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=1, suit="m"),
        ],
    )
    assert fulou_pai[2] == Fulou(
        type="minggang",
        nakipai=Pai(num=1, suit="m"),
        fuloupais=[Pai(num=1, suit="m"), Pai(num=1, suit="m"), Pai(num=1, suit="m")],
    )


def test_set_fulou_pai_from_shoupai():
    # 副露牌候補セット
    # 1
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    assert len(shoupai.waiting_fulou_pai) == 24

    # 2
    pais = create_pais(["1m"])
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    assert len(shoupai.waiting_fulou_pai) == 0
    # 3
    pais = create_pais(["1m", "2m", "5m", "9m"])
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    assert len(shoupai.waiting_fulou_pai) == 1
    # 4
    pais = create_pais(["1m", "2m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    print(shoupai.waiting_fulou_pai, "shoupai.waiting_fulou_pai")
    assert len(shoupai.waiting_fulou_pai) == 2
    assert shoupai.waiting_fulou_pai[0] == Fulou(
        type="chi",
        nakipai=Pai(num=3, suit="m"),
        fuloupais=[
            Pai(num=1, suit="m"),
            Pai(num=2, suit="m"),
        ],
    )
    assert shoupai.waiting_fulou_pai[1] == Fulou(
        type="peng",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )
    # 5
    pais = create_pais(["1m", "5m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    print(shoupai.waiting_fulou_pai, "shoupai.waiting_fulou_pai")
    assert len(shoupai.waiting_fulou_pai) == 2
    assert shoupai.waiting_fulou_pai[0] == Fulou(
        type="peng",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )
    assert shoupai.waiting_fulou_pai[1] == Fulou(
        type="minggang",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )
    # 5
    pais = create_pais(["5m", "5m", "5m", "5m"])
    shoupai = Shoupai(bingpai=pais)
    shoupai.set_fulou_pai_from_shoupai()
    print(shoupai.waiting_fulou_pai, "shoupai.waiting_fulou_pai")
    assert len(shoupai.waiting_fulou_pai) == 2
    assert shoupai.waiting_fulou_pai[0] == Fulou(
        type="peng",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )
    assert shoupai.waiting_fulou_pai[1] == Fulou(
        type="minggang",
        nakipai=Pai(num=5, suit="m"),
        fuloupais=[
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
            Pai(num=5, suit="m"),
        ],
    )


def test_regular_tenpai_ryanmen():
    # 両面待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "2s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 2
    assert Pai(suit="s", num=1) in agari_pais
    assert Pai(suit="s", num=4) in agari_pais


def test_regular_tenpai_ryanmen_2():
    # 両面待ち
    pais = create_pais(
        ["1m", "3s", "2s", "3m", "6m", "4m", "5m", "8m", "7m", "9m", "1p", "1p", "2m"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 2
    assert Pai(suit="s", num=1) in agari_pais
    assert Pai(suit="s", num=4) in agari_pais


def test_regular_tenpai_kanchan():
    # 嵌張待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1s", "3s"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 1
    assert Pai(suit="s", num=2) in agari_pais


def test_regular_tenpai_penchan():
    # 辺張待ち
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "1p", "1p", "1p", "1s", "1s", "8s", "9s"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 1
    assert Pai(suit="s", num=7) in agari_pais


def test_regular_tenpai_tanki():
    # 4面子1雀頭テンパイ（単騎待ち）
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1p", "1s"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    print(agari_pais)
    assert is_tenpai == True
    assert len(agari_pais) == 1
    assert Pai(suit="s", num=1) in agari_pais


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
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 1
    assert Pai(suit="p", num=1) in agari_pais


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
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == False
    assert len(agari_pais) == 0


def test_qidui_with_fulou():
    # 副露ありの七対子（テンパイにならない）
    bingpai = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "6s", "7m"]
    )
    fulou = [
        Fulou(
            type="chi",
            nakipai=Pai(suit="s", num=3),
            fuloupais=create_pais(["1s", "2s", "3s"]),
        )
    ]
    shoupai = Shoupai(bingpai=bingpai, fulou=fulou)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == False
    assert len(agari_pais) == 0


def test_kokushi_with_fulou():
    # 副露ありの国士無双（テンパイにならない）
    bingpai = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    fulou = [
        Fulou(
            type="chi",
            nakipai=Pai(suit="s", num=3),
            fuloupais=create_pais(["1s", "2s", "3s"]),
        )
    ]
    shoupai = Shoupai(bingpai=bingpai, fulou=fulou)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == False
    assert len(agari_pais) == 0


def test_complex_wait():
    # 複合待ちのテンパイ
    pais = create_pais(
        ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "2p", "3p", "4p", "5p", "5p"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 3
    assert Pai(suit="m", num=3) in agari_pais
    assert Pai(suit="m", num=6) in agari_pais
    assert Pai(suit="m", num=9) in agari_pais


def test_chiitoitsu_tenpai():
    # 七対子テンパイ（チートイツ）: 1m 1m 2p 2p 3s 3s 4m 4m 5p 5p 6s 6s 7z
    pais = create_pais(
        ["1m", "1m", "2p", "2p", "3s", "3s", "4m", "4m", "5p", "5p", "6s", "6s", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 1
    assert Pai(suit="z", num=7) in agari_pais


def test_kokushi_13_way_tenpai():
    # 国士無双13面待ち: 1m 9m 1p 9p 1s 9s 1z 2z 3z 4z 5z 6z 7z
    pais = create_pais(
        ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]
    )
    shoupai = Shoupai(bingpai=pais)
    is_tenpai, agari_pais = shoupai.calculate_xiangting()
    assert is_tenpai == True
    assert len(agari_pais) == 13

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
    
    