import pytest
from app.models.game import Game,Hupai
from app.models.player import Player
from app.models.pai import Pai
from app.models.shoupai import PatternResult,Fulou
from typing import Dict,Any,Literal,List,Union,TypedDict


class Kezi(TypedDict):
    yaojiu: List[List[Pai]]
    zhongzhang: List[List[Pai]]
class Duizi(TypedDict):
    yaojiu: List[List[Pai]]
    zhongzhang: List[List[Pai]]
class Jiangtou(TypedDict):
    yaojiu: List[List[Pai]]
    zhongzhang: List[List[Pai]]
class Tanki(TypedDict):
    yaojiu: List[Pai]
    zhongzhang: List[Pai]

class Shunzi(TypedDict):
    zhongzhang: List[List[Pai]]

class Bingpai(TypedDict):
    kezi: Kezi
    shunzi: Shunzi
    duizi:Duizi
    qianzhang:List[List[Pai]]
    bianzhang:List[List[Pai]]
    tanki:Tanki
    jiangtou:Jiangtou
    liangmian:List[List[Pai]]
    
   
class FulouTypes(TypedDict):
    peng: dict[Literal["yaojiu", "zhongzhang"], List[Fulou]]
    minggang: dict[Literal["yaojiu", "zhongzhang"], List[Fulou]]
    angang: dict[Literal["yaojiu", "zhongzhang"], List[Fulou]]
    chi: dict[Literal["zhongzhang"], List[Fulou]]
    
class Data(TypedDict):
    bingpai: Bingpai
    fulou: FulouTypes
    
@pytest.fixture
def test_data():
    anshunzi=[[Pai.deserialize(f"{s}{n}") for n in [i+1,i+2,i+3]] for (i,s) in enumerate(["m","p","s","s"]) ]
    mingshunzi=[Fulou.deserialize(f"chi,{s}{i+1},{s}{i+2}+{s}{i+3},shangjia")  for (i,s) in enumerate(["m","p","s","s"]) ]
    zhongzhan_anke=[[Pai.deserialize(f"{s}{i+2}") for _ in range(3)] for (i,s) in enumerate(["m","p","s","s"]) ]
    yao_anke=[[Pai.deserialize(f"{s}{1 if i % 2==0 else 9}") for _ in range(3)] for (i,s) in enumerate(["m","p","s","s"]) ]
    zhongzhan_mingke=[Fulou.deserialize(f"peng,{s}{i+2},{s}{i+2}+{s}{i+2},duimian")  for (i,s) in enumerate(["m","p","s","s"]) ]
    yao_mingke=[Fulou.deserialize(f"peng,{s}{1 if i % 2==0 else 9},{s}{1 if i % 2==0 else 9}+{s}{1 if i % 2==0 else 9},duimian")  for (i,s) in enumerate(["m","p","s","s"]) ]
    zhongzhan_angang=[Fulou.deserialize(f"angang,null,{'+'.join([f'{s}{i+2}' for _ in range(4)])},null")  for (i,s) in enumerate(["m","p","s","s"]) ]
    yao_angang=[Fulou.deserialize(f"angang,null,{'+'.join([f'{s}{1 if i % 2==0 else 9}' for _ in range(4)])},null")  for (i,s) in enumerate(["m","p","s","s"]) ]
    zhongzhan_minggang=[Fulou.deserialize(f"minggang,{s}{i+2},{'+'.join([f'{s}{i+2}' for _ in range(3)])},duimian")  for (i,s) in enumerate(["m","p","s","s"]) ]
    yao_minggang=[Fulou.deserialize(f"minggang,{s}{1 if i % 2==0 else 9},{'+'.join([f'{s}{1 if i % 2==0 else 9}' for _ in range(3)])},duimian")  for (i,s) in enumerate(["m","p","s","s"]) ]
    yao_duizi=[[Pai.deserialize(f"{s}{1 if i % 2==0 else 9}") for _ in range(2)] for (i,s) in enumerate(["m","p","s","s"]) ]
    zhongzhan_duizi=[[Pai.deserialize(f"{s}{i+2}") for _ in range(2)] for (i,s) in enumerate(["m","p","s","s"]) ]
    yao_tanki=[Pai.deserialize(f"{s}{1 if i % 2==0 else 9}")for (i,s) in enumerate(["m","p","s","s"]) ]
    zhongzhan_tanki=[Pai.deserialize(f"{s}{i+2}")  for (i,s) in enumerate(["m","p","s","s"]) ]
    liangmian=[[Pai.deserialize(f"{s}{n}") for n in [i+2,i+3]] for (i,s) in enumerate(["m","p","s","s"]) ]
    qianzhang=[[Pai.deserialize(f"{s}{n}") for n in [i+1,i+3]] for (i,s) in enumerate(["m","p","s","s"]) ]
    bianzhang=[[Pai.deserialize(f"{s}{n}") for n in [(1 if i % 2==0 else 8),(2 if i % 2==0 else 9)]] for (i,s) in enumerate(["m","p","s","s"]) ]

    data:Data = {
        "bingpai": {
            "kezi": {"yaojiu": yao_anke, "zhongzhang": zhongzhan_anke},
            "shunzi": {"zhongzhang": anshunzi},
            "duizi": {"yaojiu": yao_duizi, "zhongzhang": zhongzhan_duizi},
            "liangmian":liangmian,
            "qianzhang":qianzhang,
            "bianzhang":bianzhang,
            "tanki":{"yaojiu": yao_tanki, "zhongzhang": zhongzhan_tanki},
            "jiangtou":{"yaojiu": yao_duizi, "zhongzhang": zhongzhan_duizi}
        },
        "fulou": {
            "peng": {"yaojiu": yao_mingke, "zhongzhang": zhongzhan_mingke},
            "minggang": {"yaojiu": yao_minggang, "zhongzhang": zhongzhan_minggang},
            "angang": {"yaojiu": yao_angang, "zhongzhang": zhongzhan_angang},
            "chi": {"zhongzhang": mingshunzi},
        },
    }

    return data 

def test_game_init():
    game = Game()
    assert game.zuoci == "東"


def test_qipai(): 
    game = Game()
    game.select_zuoci()
    game.qipai()
    assert len(game.shan.pais) == 70
    for i in range(4):
        assert len(game.players[i].shoupai.bingpai) == 13
        assert game.players[i].menfeng == ["東", "南", "西", "北"][i]
    assert len(game.wangpai.baopai) == 5
    assert len(game.wangpai.libaopai) == 5
    assert len(game.wangpai.lingshangpai) == 4
    assert game.score.baopai[0]==game.wangpai.baopai[0]
    assert game.score.menfeng==["東", "南", "西", "北"]

    old_game = game.model_copy()
    print("old_game.players[0].menfeng",old_game.players[0].menfeng)
    next_game = game.next_game()
    print("old_game.players[0].menfeng,next_game.players[0].menfeng",old_game.players[0].menfeng,next_game.players[0].menfeng)
    next_game.qipai()
    for i in range(4): # 時々エラーが起きる
        assert any(next_game.players[i].shoupai.bingpai[j]!= old_game.players[i].shoupai.bingpai[j] for j in range(13))
        assert next_game.players[i].menfeng == game.get_next_feng(old_game.players[i].menfeng)
        assert len(next_game.players[i].shoupai.bingpai)==13
        assert len(old_game.players[i].shoupai.bingpai)==13

    for i in range(4):
        old_game.players[i].he.add_pai(p for p in [Pai(suit="m",num=1),Pai(suit="m",num=2),Pai(suit="m",num=3),Pai(suit="m",num=4)])
        old_game.players[i].shoupai.bingpai.append(p for p in [Pai(suit="m",num=1),Pai(suit="m",num=2),Pai(suit="m",num=3),Pai(suit="m",num=4)])
    old_game.shan.pais=[]
    old_game.wangpai.baopai=[]
    old_game.wangpai.lingshangpai=[]
    old_game.wangpai.libaopai=[]
    old_game.score.baopai=[Pai(suit="b",num=0)]
    
    next_game.qipai()
    assert len(next_game.shan.pais) == 70
    for i in range(4):
        assert len(next_game.players[i].shoupai.bingpai) == 13
        assert next_game.players[i].menfeng == [ "北", "東", "南","西"][i]
    assert len(next_game.wangpai.baopai) == 5
    assert len(next_game.wangpai.libaopai) == 5
    assert len(next_game.wangpai.lingshangpai) == 4
    assert next_game.score.baopai[0]==next_game.wangpai.baopai[0]
    assert next_game.score.menfeng==[ "北", "東", "南","西"]

def test_zimo():
    game = Game()
    game.qipai()
    shan_num=70
    for i in range(4):
        zimopai=game.zimo(i)
        assert game.players[i].shoupai.zimopai==zimopai
        assert len(game.players[i].shoupai.bingpai)==13
        shan_num-=1
        assert len(game.shan.pais) == shan_num

def test_dapai():
    game = Game()
    game.qipai()
    for i in range(4):
        for j in range(13):
            zimopai=game.zimo(i)
            dapai=game.players[i].shoupai.bingpai[0]
            game.dapai(i,dapai,0)
            assert len(game.players[i].shoupai.bingpai)==13

def test_get_next_feng():
    game = Game()
    assert game.get_next_feng("東")=="北"
    assert game.get_next_feng("南")=="東"
    assert game.get_next_feng("西")=="南"
    assert game.get_next_feng("北")=="西"
    assert game.get_next_feng("東")=="北"

def get_turn():
    game = Game()
    game.qipai()
    feng=["東", "南", "西", "北"]
    for i in  range(4):
        for mf in feng:
            game.players[i].menfeng=mf[i]
            for te in feng:
                game.zuoci=te
                assert game.get_turn(i)==["main","xiajia","duimian","shangjia"][feng.index(mf)-feng.index(te)]

def test_calculate_fanshu():
    #国士無双
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("m9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[1,1,1,1,1,1,1,1,1,1,1,1,1,1],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==102
    assert hupai.name[0]=="混老頭"
    assert hupai.name[1]=="国士無双"
    
    #七対子
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m2","m4","m4","m7","m7","m9","m9","p6","p6","s1","s1","s3"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("s3")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[2,2,2,2,2,2,2],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="七対子"
    
    
    
    #立直
    game = Game()
    game.score.zhuangfeng="東"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3"]]
    game.players[0].shoupai.zimopai=None
    game.players[0].shoupai.lizhi_flag=1
    hulepai=Pai.deserialize("p4")
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="立直"
    
    #ダブル立直
    game = Game()
    game.score.zhuangfeng="東"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3"]]
    game.players[0].shoupai.zimopai=None
    game.players[0].shoupai.lizhi_flag=2
    hulepai=Pai.deserialize("p4")
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="ダブル立直"
    
    #一発
    game = Game()
    game.score.zhuangfeng="東"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3"]]
    game.players[0].shoupai.zimopai=None
    game.players[0].shoupai.lizhi_flag=True
    hulepai=Pai.deserialize("p4")
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    game.players[0].shoupai.is_yifa=True
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="立直"
    assert hupai.name[1]=="一発"
    
    #ツモ
    game = Game()
    game.score.zhuangfeng="東"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3"]]
    game.players[0].shoupai.zimopai=Pai.deserialize("p4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="門前清自摸和"
    
    #風牌
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="西"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","z3","z3"]]
    hulepai=Pai.deserialize("z3")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="自風 西"
    
    #場牌
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="西"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","z2","z2"]]
    hulepai=Pai.deserialize("z2")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="場風 南"
    
    #役牌
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","z5","z5"]]
    hulepai=Pai.deserialize("z5")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="翻牌 白"
    
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","z6","z6"]]
    hulepai=Pai.deserialize("z6")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="翻牌 發"
    
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","z7","z7"]]
    hulepai=Pai.deserialize("z7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="翻牌 中"
    
    #タンヤオ
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m6","m7","m8","m8","m8","p6","p8"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,m2,m2+m2,duimian"]]
    hulepai=Pai.deserialize("p7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="断幺九"
    
    #平和
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="平和"
    
    #一盃口
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","p2","p3","p4","p6","p7","p8","p9","p9","p6","p8"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="一盃口"
    
    # 海底撈月
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in []]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m6","m7","m8","p2","p2","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,m2,m2+m2,duimian"]]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="海底撈月"
    
    # 河底撈魚
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in []]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m6","m7","m8","p2","p2","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,m2,m2+m2,duimian"]]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="河底撈魚"
    
    # 嶺上開花
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m6","m7","m8","p2","p2","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["minggang,m2,m2+m2+m2,duimian"]]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0],["lingshang"])
    assert hupai.fanshu==1
    assert hupai.name[0]=="嶺上開花"
    
    # 槍槓
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m6","m7","m8","p2","p2","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["minggang,m2,m2+m2+m2,duimian"]]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0],["qianggang"])
    assert hupai.fanshu==1
    assert hupai.name[0]=="槍槓"
    
    #三色同順
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","p1","p2","p3","p3","p4","p5","p6","p6","s1","s2",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("s3")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="三色同順"
    
    #三色同順 （食い下がり）
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","p5","p5","p5","p6","p6","s1","s2",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,p1,p2+p3,shangjia"]]
    hulepai=Pai.deserialize("s3")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="三色同順"
    
    #一気通貫
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","p1","p2","p3","p4","p5","p6","p7","p7","p7","p9",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="一気通貫"
    
    #三色同順 （食い下がり）
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","p4","p5","p6","p7","p7","p7","p9",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,p1,p2+p3,shangjia"]]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="一気通貫"
    
    #対々和
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","p7","p7","p9","p9",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,p1,p1+p1,shangjia","peng,z3,z3+z3,duimian"]]
    hulepai=Pai.deserialize("p9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="対々和"
    
    #ホンイツ
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m2","m3","m4","m7","m7","m7","z3","z3","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==3
    assert hupai.name[0]=="混一色"
    
    #ホンイツ（食い下がり）
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m2","m3","m4","m7","m7","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,z3,z3+z3,xiajia"]]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="混一色"
    
    #三暗刻
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","p7","p7","p7","z3","z3","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,m1,m2+m3,shangjia"]]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="三暗刻"
    
    #三色同刻
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","p1","p1","p1","m6","m6","m7","m8"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,s1,s1+s1,xiajia"]]
    hulepai=Pai.deserialize("m9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="三色同刻"
    
    #混老頭
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m9"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,p1,p1+p1,shangjia","peng,s1,s1+s1,xiajia","peng,z1,z1+z1,xiajia","peng,z4,z4+z4,duimian"]]
    hulepai=Pai.deserialize("m9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[2],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==4
    assert hupai.name[0]=="対々和"
    assert hupai.name[1]=="混老頭"
    
    #チャンタ
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m7","m8","m9","p1","p2","p3","z3","z3","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="混全帯幺九"
    
    #チャンタ(食い下がり)
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m7","m8","m9","p1","p2","p3","z3","z3","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,m2,m1+m3,shangjia"]]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==1
    assert hupai.name[0]=="混全帯幺九"
    
    #小三元
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","p3","p4","p5","z5","z5","z5","z6","z6","z7","z7",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("z7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==4
    assert hupai.name[0]=="翻牌 白"
    assert hupai.name[1]=="翻牌 中"
    assert hupai.name[2]=="小三元"
    
    #三槓子
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m7","m8","m9","p3"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["angang,null,m3+m3+m3+m3,null","jiagang,p4,p4+p4+p4,xiajia","minggang,s5,s5+s5+s5,duimian"]]
    hulepai=Pai.deserialize("p3")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,2],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="三槓子"
    
    #純チャン
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m7","m8","m9","p1","p2","p3","p9","p9","s1","s1",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("s1")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==3
    assert hupai.name[0]=="純全帯幺九"
    
    #純チャン(食い下がり)
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m7","m8","m9","p1","p2","p3","p9","p9","s1","s1",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,m3,m1+m2,shangjia"]]
    hulepai=Pai.deserialize("s1")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==2
    assert hupai.name[0]=="純全帯幺九"
    
    #二盃口
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m2","m3","m4","p6","p7","p8","p9","p9","p6","p8"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==3
    assert hupai.name[0]=="二盃口"
    
    #清一色
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m2","m3","m4","m7","m7","m7","m8","m8","m9","m9",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("m9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==6
    assert hupai.name[0]=="清一色"
    
    #清一色（食い下がり）
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m7","m7","m7","m8","m8","m9","m9",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,m1,m2+m3,shangjia",]]
    hulepai=Pai.deserialize("m9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==5
    assert hupai.name[0]=="清一色"
    
    #天和
    game = Game()
    game.score.zhuangfeng="東"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in []]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==101
    assert hupai.name[0]=="門前清自摸和"
    assert hupai.name[1]=="天和"
    
    #地和
    game = Game()
    game.score.zhuangfeng="東"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in []]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==101
    assert hupai.name[0]=="門前清自摸和"
    assert hupai.name[1]=="地和"
    
    #緑一色
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["s2","s3","s4","s6","s6","s8","s8"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["chi,s3,s2+s4,shangjia","peng,z6,z6+z6,duimian"]]
    hulepai=Pai.deserialize("s8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==103
    assert hupai.name[0]=="翻牌 發"
    assert hupai.name[1]=="混一色"
    assert hupai.name[2]=="緑一色"
    
    #大三元
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","z6","z6","z6","p1","p1","z7","z7",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,z5,z5+z5,duimian"]]
    hulepai=Pai.deserialize("z7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==103
    assert hupai.name[0]=="翻牌 發"
    assert hupai.name[1]=="翻牌 中"
    assert hupai.name[2]=="翻牌 白"
    assert hupai.name[3]=="大三元"
    
    #小四喜
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="西"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","z2","z2","z2","z3","z3","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,duimian"]]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==103
    assert hupai.name[0]=="場風 南"
    assert hupai.name[1]=="混一色"
    assert hupai.name[2]=="小四喜"
    
    #緑一色
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["z2","z2","z2","z4","z4","z7","z7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,shangjia","peng,z6,z6+z6,duimian"]]
    hulepai=Pai.deserialize("z7")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==106
    assert hupai.name[0]=="自風 南"
    assert hupai.name[1]=="場風 南"
    assert hupai.name[2]=="翻牌 中"
    assert hupai.name[3]=="翻牌 發"
    assert hupai.name[4]=="対々和"
    assert hupai.name[5]=="字一色"
    
    
    #九蓮宝燈
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m2","m3","m4","m5","m6","m7","m8","m8","m9","m9",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("m9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==106
    assert hupai.name[0]=="清一色"
    assert hupai.name[1]=="九蓮宝燈"
    
    #四暗刻
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m3","m3","p7","p7","p7","z3","z3","z4","z4"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==103
    assert hupai.name[0]=="門前清自摸和"
    assert hupai.name[1]=="対々和"
    assert hupai.name[2]=="四暗刻"
    
    #清老頭
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","s1","s1","s9","s9"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,m9,m9+m9,shangjia","peng,p1,p1+p1,duimian"]]
    hulepai=Pai.deserialize("s9")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==102
    assert hupai.name[0]=="対々和"
    assert hupai.name[1]=="清老頭"
    
    #四槓子
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["p3"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["angang,null,m3+m3+m3+m3,null","jiagang,p4,p4+p4+p4,xiajia","minggang,s5,s5+s5+s5,duimian","minggang,s9,s9+s9+s9,shangjia"]]
    hulepai=Pai.deserialize("p3")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[2],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==102
    assert hupai.name[0]=="対々和"
    assert hupai.name[1]=="四槓子"
    
    #大四喜
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="西"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["p2","p2","z4","z4",]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,duimian","peng,z2,z2+z2,duimian","peng,z3,z3+z3,duimian"]]
    hulepai=Pai.deserialize("z4")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game._calculate_fanshu(0,game.players[0].shoupai.hule_candidates[0])
    assert hupai.fanshu==106
    assert hupai.name[0]=="自風 西"
    assert hupai.name[1]=="場風 南"
    assert hupai.name[2]=="混一色"
    assert hupai.name[3]=="対々和"
    assert hupai.name[4]=="大四喜"

def test_calculate_hu(test_data):
    #平和・自摸
    game = Game()
    game.zuoci="東"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=2
    input_hupai.name+=["平和","門前清自摸和"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m3","m4","m5","m7","m8","m9","p1","p1","p2","p3","p4"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==20
    
    #七対子
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=2
    input_hupai.name+=["七対子"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m1","m3","m3","m4","m4","m7","m7","p1","p1","p2","p2","p3","p3"]],[2,2,2,2,2,2,2])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==25
    
    #国士
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=100
    input_hupai.name+=["国士無想"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7","z7"]],[1,1,1,1,1,1,1,1,1,1,1,1,1,1])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==20
    
    #暗刻含み
    ##中帳牌 ロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["一盃口"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m1","m2","m3","m8","m8","m8","p1","p1","p2","p3","p4"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==40
    
    ##ヤオチュー牌 ロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["一盃口"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m1","m2","m3","m9","m9","m9","p1","p1","p2","p3","p4"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==40
    
    #両面ロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["平和"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m2","m3","m4","m7","m8","m9","p1","p1","p2","p3","p4"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==30
    
    #カンチャンロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["一盃口"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m1","m2","m3","m7","m8","m9","p1","p1","p2","p4","p3"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==40
    
    #ペンチャンロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["一盃口"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m1","m2","m3","m7","m8","m9","p1","p1","p8","p9","p7"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==40
    
    #単騎ロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["一盃口"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m1","m2","m3","m7","m8","m9","p1","p2","p3","p9","p9"]],[3,3,3,3,2])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==40
    
    #シャンポンロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["一盃口"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m2","m3","m1","m2","m3","m7","m8","m9","p1","p1","p8","p8","p8"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==40
    
    #立直
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["立直"]
    input_hupai.pat=PatternResult([Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p2","p3","p4"]],[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==50
    
    #4順子+役無雀頭+両面+ロン
    game = Game()
    game.zuoci="南"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["立直"]
    bingpai=sum(test_data["bingpai"]["shunzi"]["zhongzhang"][:3], [])+test_data["bingpai"]["jiangtou"]["zhongzhang"][0]+test_data["bingpai"]["liangmian"][0]+[Pai.deserialize("m5")]
    input_hupai.pat=PatternResult(bingpai,[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==30
    print(input_hupai.pat.pais)
    
    #4順子+役無雀頭+両面+ツモ
    game = Game()
    game.zuoci="東"
    game.players[0].menfeng="東"
    game.score.zhuangfeng="東"
    game.players[0].shoupai.fulou=[]
    input_hupai=Hupai()
    input_hupai.fanshu=1
    input_hupai.name+=["立直","平和","門前清自摸和"]
    bingpai=sum(test_data["bingpai"]["shunzi"]["zhongzhang"][:3], [])+test_data["bingpai"]["jiangtou"]["zhongzhang"][0]+test_data["bingpai"]["liangmian"][0]+[Pai.deserialize("m5")]
    input_hupai.pat=PatternResult(bingpai,[3,3,3,2,3])
    result_hupai=game._calculate_hu(0,input_hupai)
    assert result_hupai.hu ==20

def test_calcualate_defen():
    game = Game()
    game.zuoci="南"
    for i,f in enumerate(["東","南","西","北"]):
        game.players[i].menfeng=f
    
    for num in range(4):
        for teban in ["東","南","西","北"]:
            game.zuoci=teban
            for fanshu in range(1,14):
                for hu in range(20,120,10):
                    input_hupai=Hupai(fanshu=fanshu,hu=hu)
                    result_defen=game._calcualate_defen(num,input_hupai)
                    #合計が0
                    assert sum(result_defen)==0
                    for i in range(4):
                        #アガリプレイヤーの点数はプラス
                        if i==num:
                            assert result_defen[i]>0
                        #アガリ以外のプレイヤー
                        else:
                            #放銃者はマイナス
                            if teban==game.players[i].menfeng:
                                assert result_defen[i]<0
                            else:
                                #ツモアガリのときはマイナス
                                if teban==game.players[num].menfeng:
                                    assert result_defen[i]<0
                                else:
                                    assert result_defen[i]==0

def test_pingju():
    game = Game()
    # 基本的な配分パターンのテスト
    test_cases = [
        ([0, 0, 1, 1], [1500, 1500, -1500, -1500],[26500, 26500, 23500, 23500],),
        ([0, 1, 1, 1], [3000, -1000, -1000, -1000],[28000, 24000, 24000, 24000]),
        ([1, 0, 2, 3], [-1000, 3000, -1000, -1000],[24000, 28000, 24000, 24000]),
        ([0, 0, 0, 1], [1000, 1000, 1000, -3000],[26000, 26000, 26000, 22000]),
        ([0, 0, 0, 0], [0, 0, 0, 0],[25000, 25000, 25000, 25000]),
        ([1, 2, 3, 4], [0, 0, 0, 0],[25000, 25000, 25000, 25000])
    ]
    
    for input_array, expected_pingju_defen,expected_defen in test_cases:
        game.score.defen=[25000, 25000, 25000, 25000]
        for i in range(4):
            game.players[i].shoupai.xiangting=int(input_array[i])
        result = game.pingju()
        assert result==expected_pingju_defen
        assert sum(result)==0
        assert game.score.defen==expected_defen

def test_lizhi():
    #立直
    game=Game()
    game.score.zhuangfeng="東"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="東"
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p3","p4"]]
    game.players[0].shoupai.zimopai=Pai.deserialize("z1")
    game.lizhi(0,game.players[0].shoupai.zimopai,99)
    assert game.players[0].shoupai.lizhi_flag==1
    assert game.players[0].shoupai.is_yifa==True
    assert game.players[0].shoupai.zimopai==None
    assert len(game.players[0].shoupai.hule_candidates)==2
    
    #ダブル立直
    game=Game()
    game.score.zhuangfeng="南"
    game.zuoci="南"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    game.players[0].menfeng="南"
    game.players[0].he.pais=[Pai.deserialize(s) for s in []]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3","m4","m5","m8","m8","m8","p1","p1","p3","p4"]]
    game.players[0].shoupai.zimopai=Pai.deserialize("z1")
    game.lizhi(0,game.players[0].shoupai.zimopai,99)
    assert game.players[0].shoupai.lizhi_flag==2
    assert game.players[0].shoupai.is_yifa==True
    assert game.players[0].shoupai.zimopai==None
    assert len(game.players[0].shoupai.hule_candidates)==2
    
def test_hule():
    #平和ロンアガリ
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    for p, mf in zip(game.players, ["南","西","北","東"]):
        p.menfeng = mf
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    hupai=game.hule(0,hulepai)
    assert game.score.defen==[26000,25000,25000,24000]
    assert hupai.fanshu==1
    assert hupai.hu==30
    assert hupai.name==["平和"]
    
    #フリテンアガリ
    game = Game()
    game.score.zhuangfeng="南"
    game.zuoci="東"
    game.shan.pais=[Pai.deserialize(s) for s in ["z1"]]
    for p, mf in zip(game.players, ["南","西","北","東"]):
        p.menfeng = mf
    game.players[0].he.pais=[Pai.deserialize(s) for s in ["z2","p8"]]
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.fulou=[Fulou.deserialize(s) for s in []]
    hulepai=Pai.deserialize("p8")
    game.players[0].shoupai.lizhi_flag=False
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[hulepai])]
    with pytest.raises(ValueError):
        assert game.hule(0,hulepai)
     
def test_is_tingpaiqing():
    #捨て牌なし
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    assert game.is_tingpaiqing
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f"
    
    #捨て牌あり、立直なし、フリテンなし
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["m","p","s","z"]):
        for n in range(1,8):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f"
    
    #捨て牌あり、立直なし、フリテンあり（自家捨て牌）
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["p","m","s","z"]):
        for n in range(1,6):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert not game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f+b0"
    
    #捨て牌あり、立直なし、フリテンあり(他家捨て牌)
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["m","p","s","z"]):
        for n in range(1,6):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert not game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f+b0"
    
    
    #捨て牌あり、立直あり、フリテンなし
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    game.players[0].shoupai.lizhi_flag=1
    game.players[0].he.lizhi_num=5
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["m","p","s","z"]):
        for n in range(1,8):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f"
    
    #捨て牌あり、立直あり、フリテンあり（自家捨て牌）
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    game.players[0].shoupai.lizhi_flag=1
    game.players[0].he.lizhi_num=5
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["p","m","s","z"]):
        for n in range(1,8):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert not game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f+b0"
    
    #捨て牌あり、立直あり、フリテンあり(他家捨て牌)
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    game.players[0].shoupai.lizhi_flag=1
    game.players[0].he.lizhi_num=0
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["東", "南", "西", "北"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["m","p","s","z"]):
        for n in range(1,8):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert not game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f+b0"
    
    #打牌順序考慮
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m5","m6","m7","p1","p2","p3","m1","m1","p6","p7"]]
    game.players[0].shoupai.xiangting=0
    hulepai=[Pai.deserialize(s) for s in ["p5","p8"]]
    game.players[0].shoupai.hule_candidates=[PatternResult(nums=[3,3,3,2,3],pais=game.players[0].shoupai.bingpai+[p]) for p in hulepai]
    for player_id,f in enumerate(["北", "東", "南", "西"]):
        game.players[player_id].menfeng=f
    for player_id,s in enumerate(["m","p","s","z"]):
        for n in range(1,5):
            game.players[player_id].he.pais.append(Pai.deserialize(f"{s}{n}"))
    assert game.is_tingpaiqing(0)
    game.players[1].he.pais.append(Pai.deserialize(f"p5"))
    assert not game.is_tingpaiqing(0)
    assert game.get_serialized_hule_pai(0,True)=="p5f+p8f+b0"

def test_fulou():
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m1","m2","p3","p3","p3","p5","p5","p5","p6","p7"]]
    fulou_candidates=[Fulou.deserialize(f) for f in ["peng,p5,p5+p5,null","chi,p8,p6+p7,null","minggang,p3,p3+p3+p3,null","angang,null,m1+m1+m1+m1,null","jiagang,p5,p5+p5+p5,null"]]
    game.players[0].shoupai.fulou_candidates=fulou_candidates
    peng=game.players[0].shoupai.fulou_candidates[0].model_copy(update={"position":"duimian"})
    chi=game.players[0].shoupai.fulou_candidates[1].model_copy(update={"position":"shangjia"})
    minggang=game.players[0].shoupai.fulou_candidates[2].model_copy(update={"position":"xiajia"})
    angang=game.players[0].shoupai.fulou_candidates[3].model_copy()
    jiagang=game.players[0].shoupai.fulou_candidates[4].model_copy(update={"position":"duimian"})
    game.fulou(0,peng)
    assert game.players[0].shoupai.fulou[0].serialize()==peng.serialize()
    game.players[0].shoupai.fulou_candidates=fulou_candidates
    game.fulou(0,chi)
    assert game.players[0].shoupai.fulou[1].serialize()==chi.serialize()
    game.players[0].shoupai.fulou_candidates=fulou_candidates
    game.fulou(0,minggang)
    assert game.players[0].shoupai.fulou[2].serialize()==minggang.serialize()
    game.players[0].shoupai.fulou_candidates=fulou_candidates
    game.fulou(0,angang)
    assert game.players[0].shoupai.fulou[3].serialize()==angang.serialize()
    game.players[0].shoupai.fulou_candidates=fulou_candidates
    game.fulou(0,jiagang)
    assert game.players[0].shoupai.fulou[0].serialize()==jiagang.serialize()
    assert len(game.players[0].shoupai.bingpai)==1
    
    #一発けし
    game = Game()
    game.players[0].shoupai.bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m1","m2","p3","p3","p3","p5","p5","p5","p6","p7"]]
    for i in range(4):
        game.players[i].shoupai.is_yifa=True
    fulou_candidates=[Fulou.deserialize(f) for f in ["peng,p5,p5+p5,null","chi,p8,p6+p7,null","minggang,p3,p3+p3+p3,null","angang,null,m1+m1+m1+m1,null","jiagang,p5,p5+p5+p5,null"]]
    game.players[0].shoupai.fulou_candidates=fulou_candidates
    peng=game.players[0].shoupai.fulou_candidates[0].model_copy(update={"position":"duimian"})
    game.fulou(0,peng)
    for i in range(4):
        assert not game.players[i].shoupai.is_yifa

def test_lingshangzimo():
    game = Game()
    game.wangpai.baopai=[Pai.deserialize(p) for p in ["m1","m2","m3","m4","m5"]]
    game.wangpai.lingshangpai=[Pai.deserialize(p) for p in ["p1","p2","p3","p4"]]
    game.wangpai.flipped_baopai=[True if i==0 else False for i in range(5)]
    for i in range(4):
        lingshangzimo,baopai=game.lingshangzimo(0)
        assert game.players[0].shoupai.zimopai.serialize()==f"p{i+1}f"
        assert lingshangzimo.serialize()==f"p{i+1}f"
        assert baopai.serialize()==f"m{i+2}f"
        game.players[0].shoupai.zimopai=None
    #5回目の嶺上ツモはエラー
    with pytest.raises(ValueError):
        lingshangzimo,baopai=game.lingshangzimo(0)
        
        
    
    
    
    