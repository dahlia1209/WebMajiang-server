import pytest
from app.models.game import Game
from app.models.player import Player
from app.models.pai import Pai


def test_game_init():
    game = Game()
    assert game.teban == "東"


def test_qipai():
    game = Game()
    game.players = [Player() for _ in range(4)]
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
    next_game = Game()
    next_game.players = [Player() for _ in range(4)]
    next_game.qipai()
    for i in range(4):
        assert (
            next_game.players[i].shoupai.bingpai[0]
            != old_game.players[i].shoupai.bingpai[0]
            or next_game.players[i].shoupai.bingpai[12]
            != old_game.players[i].shoupai.bingpai[12]
        )
        assert next_game.players[i].menfeng == old_game.players[i].menfeng
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
    
    next_game.qipai(old_game)
    assert len(next_game.shan.pais) == 70
    for i in range(4):
        assert len(next_game.players[i].shoupai.bingpai) == 13
        assert next_game.players[i].menfeng == [ "南", "西", "北","東"][i]
    assert len(next_game.wangpai.baopai) == 5
    assert len(next_game.wangpai.libaopai) == 5
    assert len(next_game.wangpai.lingshangpai) == 4
    assert next_game.score.baopai[0]==next_game.wangpai.baopai[0]
    assert next_game.score.menfeng==["南", "西", "北","東"]

def test_zimo():
    game = Game(players=[Player() for _ in range(4)])
    game.qipai()
    shan_num=70
    for i in range(4):
        zimopai=game.zimo(i)
        assert game.players[i].shoupai.zimopai==zimopai
        assert len(game.players[i].shoupai.bingpai)==13
        shan_num-=1
        assert len(game.shan.pais) == shan_num

def test_dapai():
    game = Game(players=[Player() for _ in range(4)])
    game.qipai()
    for i in range(4):
        for j in range(13):
            dapai=game.players[i].shoupai.bingpai[0]
            game.dapai(i,dapai,0)
            assert len(game.players[i].shoupai.bingpai)==(12-j)

def test_next_teban():
    game = Game(players=[Player() for _ in range(4)])
    game.qipai()
    assert game.next_teban()=="南"
    assert game.next_teban()=="西"
    assert game.next_teban()=="北"
    assert game.next_teban()=="東"
    assert game.next_teban()=="南"

def get_turn():
    game = Game(players=[Player() for _ in range(4)])
    game.qipai()
    feng=["東", "南", "西", "北"]
    for i in  range(4):
        for mf in feng:
            game.players[i].menfeng=mf[i]
            for te in feng:
                game.teban=te
                assert game.get_turn(i)==["main","xiajia","duimian","shangjia"][feng.index(mf)-feng.index(te)]
    

    

    
    