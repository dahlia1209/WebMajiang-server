import pytest
from app.models.shoupai import Shoupai, Fulou
from app.models.pai import Pai

def test_fulou_serialize_and_deserialize():
    fulou=Fulou(type="peng")
    assert fulou.serialize()=="peng,null,null,null"
    fulou=Fulou(type="peng",nakipai=Pai(suit="m",num=3),menpais=[Pai.deserialize("m3"),Pai.deserialize("m3")],position="duimian")
    assert fulou.serialize()=="peng,m3f,m3f+m3f,duimian"
    fulou=Fulou(type="chi",nakipai=Pai(suit="m",num=1),menpais=[Pai.deserialize("m2"),Pai.deserialize("m3")],position="shangjia")
    assert fulou.serialize()=="chi,m1f,m2f+m3f,shangjia"
    fulou=Fulou(type="angang",menpais=[Pai.deserialize("z1") for _ in range(4)])
    assert fulou.serialize()=="angang,null,z1f+z1f+z1f+z1f,null"
    
    fulou=Fulou.deserialize("peng,null,null,null")
    assert fulou==Fulou(type="peng")
    fulou=Fulou.deserialize("peng,m3f,m3f+m3f,duimian")
    assert fulou==Fulou(type="peng",nakipai=Pai(suit="m",num=3),menpais=[Pai.deserialize("m3"),Pai.deserialize("m3")],position="duimian")
    fulou=Fulou.deserialize("chi,m1f,m2f+m3f,shangjia")
    assert fulou==Fulou(type="chi",nakipai=Pai(suit="m",num=1),menpais=[Pai.deserialize("m2"),Pai.deserialize("m3")],position="shangjia")
    fulou=Fulou.deserialize("angang,null,z1f+z1f+z1f+z1f,null")
    assert fulou==Fulou(type="angang",menpais=[Pai.deserialize("z1") for _ in range(4)])
 
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
        shoupai.lizhi_flag=True
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
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 13
    copy_bingpai=[p for p in bingpai]
    for pat in xiangting_result.hule_candidates:
        copy_bingpai.remove(pat.pais[-1])
    
    #国士単騎待ち
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7"]]
    for i,p in enumerate(bingpai):
        copy_bingpai=[p for p in bingpai]
        copy_bingpai[i]=bingpai[i-1]
        shoupai = Shoupai(bingpai=copy_bingpai)
        xiangting_result = shoupai._get_kokushi_xiangting()
        assert xiangting_result.xiangting==0
        assert len(xiangting_result.best_candidates) == 1
        assert len(xiangting_result.hule_candidates) == 1
        assert xiangting_result.hule_candidates[0].pais[-1] == bingpai[i]
        
    #国士シャンテン数確認
    yaojiupai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4","z5","z6","z7"]]
    zhongzhangpai=[Pai.deserialize(s) for s in ["m2","m4","m6","m8","p2","p4","p6","p8","s2","s4","s6","s8","s5"]]
    for i in range(13):
        bingpai=zhongzhangpai[:i]+yaojiupai[i:]
        shoupai = Shoupai(bingpai=bingpai)
        xiangting_result = shoupai._get_kokushi_xiangting()
        assert xiangting_result.xiangting==i
        assert len(xiangting_result.best_candidates) == 1
    
    #副露ありのシャン点数
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4"]]
    fulou=[Fulou.deserialize("peng,z5,z5+z5,duimian")]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_kokushi_xiangting()
    assert xiangting_result.xiangting==99
    assert len(xiangting_result.best_candidates) == 0
    assert len(xiangting_result.hule_candidates) == 0
    
def test_get_qiduizi_xiangting():
    #七対子テンパイ
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","p1","p1","s1","s1","z1","z1","z3","z3","z5","z5","z7"]]
    shoupai = Shoupai(bingpai=bingpai)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 1
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("z7")
    
    #槓子があるときはリャンシャンテン以上
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","p1","p1","s1","s1","z1","z1","z3","z3","z3","z3","z7"]]
    shoupai = Shoupai(bingpai=bingpai)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result.xiangting==2
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 0
    
    #暗刻があるときはテンパイではない
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","p1","p1","s1","s1","z1","z1","z2","z2","z3","z3","z3"]]
    shoupai = Shoupai(bingpai=bingpai)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 0
    
    #暗刻+槓子
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","p1","p1","s1","s1","z1","z1","z1","z3","z3","z3","z3"]]
    shoupai = Shoupai(bingpai=bingpai)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result.xiangting==3
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 0
    
    #七対子シャン点数確認
    single_list=[Pai.deserialize(s) for s in ["p1","p2","p3","p4","p5","p6","p7","p8","p9","z1","z2","z3","z4"]]
    duizi_list=[Pai.deserialize(s) for s in ["m1","m1","m2","m2","m3","m3","m4","m4","m5","m5","m6","m6"]]
    for i in range(7):
        bingpai=duizi_list[:i*2]+single_list[i*2:]
        shoupai = Shoupai(bingpai=bingpai)
        xiangting_result = shoupai._get_qiduizi_xiangting()
        assert xiangting_result.xiangting==6-i
        assert len(xiangting_result.best_candidates) == 1
    
    #副露ありのシャン点数
    bingpai=[Pai.deserialize(s) for s in ["m1","m9","p1","p9","s1","s9","z1","z2","z3","z4"]]
    fulou=[Fulou.deserialize("peng,z5,z5+z5,duimian")]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_qiduizi_xiangting()
    assert xiangting_result.xiangting==99
    assert len(xiangting_result.best_candidates) == 0
    assert len(xiangting_result.hule_candidates) == 0

def test_get_mianzi_xiangting():
    #単騎待ち
    bingpai=[Pai.deserialize(s) for s in ["m1"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia","angang,null,z4+z4+z4+z4,null"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 1
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    
    #3副露
    ##テンパイ:両面
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m3","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 2
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m5")
    
    ##テンパイ:ペンチャン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m8","m9"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 1
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m6","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 1
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 1
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:シャンポン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m7","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 1
    assert len(xiangting_result.hule_candidates) == 2
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:ノベタン
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 2
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    
    ##テンパイ:ペンチャン+単騎
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m2"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 2
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    
    ##テンパイ:カンチャン+単騎
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m3"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 2
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    
    ##テンパイ:両面+単騎
    bingpai=[Pai.deserialize(s) for s in ["m2","m2","m2","m3"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 3
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    
    ##イーシャンテン:雀頭あり
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m6","m9"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 1
    assert xiangting_result.best_candidates[0].nums == [2,1,1]
    assert len(xiangting_result.hule_candidates) == 0
    
    ##イーシャンテン:雀頭なし
    bingpai=[Pai.deserialize(s) for s in ["m1","m3","m5","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 1
    assert xiangting_result.best_candidates[0].nums == [2,2]
    assert len(xiangting_result.hule_candidates) == 0
    
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m5","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 1
    assert xiangting_result.best_candidates[0].nums == [2,1,1]
    assert len(xiangting_result.hule_candidates) == 0
    
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m1"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 2
    assert xiangting_result.best_candidates[0].nums == [3,1]
    assert xiangting_result.best_candidates[1].nums == [2,2]
    assert len(xiangting_result.hule_candidates) == 0
    
    #リャンシャンテン
    bingpai=[Pai.deserialize(s) for s in ["z1","z2","z3","z4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==2
    assert len(xiangting_result.best_candidates) == 1
    assert xiangting_result.best_candidates[0].nums == [1,1,1,1]
    assert len(xiangting_result.hule_candidates) == 0
    
    #2副露
    ##テンパイ:両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m5","m6","z7","z7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 4
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+単騎+単騎
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m5","m6","m7","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 3
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+単騎+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m5","m5","m6","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 4
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:シャンポン+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m4","m4","m4","m7","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 4
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m2","m3","m3","m3","m4","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 5
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+両面+両面+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m4","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 4
    assert len(xiangting_result.hule_candidates) == 6
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[5].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+両面+カンチャン+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 4
    assert len(xiangting_result.hule_candidates) == 5
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m7")
    
    ##テンパイ:単騎+単騎+両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m6","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 4
    assert len(xiangting_result.hule_candidates) == 6
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result.hule_candidates[5].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m6","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 2
    assert len(xiangting_result.hule_candidates) == 2
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+カンチャン+両面
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m5","m5","m6","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 4
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+単騎+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m5","m6","m7","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 3
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m8")
    
    ##テンパイ:単騎+シャンポン+両面
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m4","m5","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 5
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m6")
    
    ##テンパイ:単騎+シャンポン+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m4","m4","m4","m5","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 4
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    
    ##テンパイ:単騎+シャンポン+両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m5","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 4
    assert len(xiangting_result.hule_candidates) == 7
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[5].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[6].pais[-1] == Pai.deserialize("m6")
    
    ##テンパイ:単騎+シャンポン+両面+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m4","m4","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 4
    assert len(xiangting_result.hule_candidates) == 6
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[5].pais[-1] == Pai.deserialize("m6")
    
    ##テンパイ:単騎+カンチャン+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m5","m7","m7","m7"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 3
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m6")
    
    ##テンパイ:単騎+両面+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m4","m5","m5","m5","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 4
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m6")
    
    ##テンパイ:単騎+両面+両面
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m4","m4","m4","m4","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 3
    assert len(xiangting_result.hule_candidates) == 5
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m6")
    
    ##テンパイ:単騎+単騎+両面+カンチャン
    bingpai=[Pai.deserialize(s) for s in ["m3","m4","m4","m4","m4","m5","m6"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 4
    assert len(xiangting_result.hule_candidates) == 5
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m6")
    
    ##1シャンテン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m1","m4","m4","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 2
    assert xiangting_result.best_candidates[0].nums == [3,3,1]
    assert xiangting_result.best_candidates[1].nums == [3,2,2]
    assert len(xiangting_result.hule_candidates) == 0
    
    bingpai = [Pai.deserialize(s) for s in ["m1","m2","m3","m4","m5","p1","p2",]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian",]]
    zimopai=Pai.deserialize("z7")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==1
    assert len(xiangting_result.best_candidates) == 2
    assert xiangting_result.best_candidates[0].nums == [3,2,2]
    assert xiangting_result.best_candidates[1].nums == [3,2,2]
    assert len(xiangting_result.hule_candidates) == 0
    
    #1副露
    ##テンパイ:単騎+単騎+両面+両面+両面+両面+シャンポン
    bingpai=[Pai.deserialize(s) for s in ["m3","m3","m3","m4","m5","m6","m7","m8","m8","m8"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia"]]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 7
    assert len(xiangting_result.hule_candidates) == 12
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[5].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[6].pais[-1] == Pai.deserialize("m6")
    assert xiangting_result.hule_candidates[7].pais[-1] == Pai.deserialize("m6")
    assert xiangting_result.hule_candidates[8].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result.hule_candidates[9].pais[-1] == Pai.deserialize("m8")
    assert xiangting_result.hule_candidates[10].pais[-1] == Pai.deserialize("m8")
    assert xiangting_result.hule_candidates[11].pais[-1] == Pai.deserialize("m9")
    
    
    
    #メンゼン
    ##テンパイ:単騎+単騎+単騎+ペンチャン+ペンチャン+両面+両面+両面+両面+シャンポン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m2","m3","m4","m5","m6","m7","m8","m9","m9","m9"]]
    fulou=[Fulou.deserialize(s) for s in []]
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou)
    xiangting_result = shoupai._get_mianzi_xiangting()
    assert xiangting_result.xiangting==0
    assert len(xiangting_result.best_candidates) == 10
    assert len(xiangting_result.hule_candidates) == 15
    assert xiangting_result.hule_candidates[0].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[1].pais[-1] == Pai.deserialize("m1")
    assert xiangting_result.hule_candidates[2].pais[-1] == Pai.deserialize("m2")
    assert xiangting_result.hule_candidates[3].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[4].pais[-1] == Pai.deserialize("m3")
    assert xiangting_result.hule_candidates[5].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[6].pais[-1] == Pai.deserialize("m4")
    assert xiangting_result.hule_candidates[7].pais[-1] == Pai.deserialize("m5")
    assert xiangting_result.hule_candidates[8].pais[-1] == Pai.deserialize("m6")
    assert xiangting_result.hule_candidates[9].pais[-1] == Pai.deserialize("m6")
    assert xiangting_result.hule_candidates[10].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result.hule_candidates[11].pais[-1] == Pai.deserialize("m7")
    assert xiangting_result.hule_candidates[12].pais[-1] == Pai.deserialize("m8")
    assert xiangting_result.hule_candidates[13].pais[-1] == Pai.deserialize("m9")
    assert xiangting_result.hule_candidates[14].pais[-1] == Pai.deserialize("m9")
    
def test_comupute_lizhi_candidates():
    #テンパイ:単騎+単騎+単騎+ペンチャン+ペンチャン+両面+両面+両面+両面+シャンポン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m2","m3","m4","m5","m6","m7","m8","m9","m9","m9"]]
    fulou=[Fulou.deserialize(s) for s in []]
    zimopai=Pai.deserialize("m1")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai,xiangting=0)
    xiangting_result = shoupai._get_mianzi_xiangting()
    shoupai.bingpai_candidates=xiangting_result.best_candidates
    shoupai.hule_candidates=xiangting_result.hule_candidates
    lizhi_pai = shoupai._comupute_lizhi_candidates()
    print("lizhi_pai",[p.serialize() for p in lizhi_pai])
    # print("pais,nums",[("+".join([p.serialize() for p in pat.pais]),pat.nums) for pat in lizhi_pai])
    assert len(lizhi_pai)==9
    
    shoupai.zimopai=Pai.deserialize("z1")
    lizhi_pai = shoupai._comupute_lizhi_candidates()
    assert len(lizhi_pai)==4
    
    #
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m3","m3","m5","m5","m7","m7","m9","m9","z1","z1","z3"]]
    fulou=[Fulou.deserialize(s) for s in []]
    zimopai=Pai.deserialize("z4")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai,xiangting=0)
    xiangting_result = shoupai._get_mianzi_xiangting()
    shoupai.bingpai_candidates=xiangting_result.best_candidates
    shoupai.hule_candidates=xiangting_result.hule_candidates
    lizhi_pai = shoupai._comupute_lizhi_candidates()
    
    assert len(lizhi_pai)==2

def test_compute_fulou_candidates ():
    #なし
    bingpai=[Pai.deserialize(s) for s in ["m1"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia","peng,z4,z4+z4,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==0

    #ポン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m4","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==2
    assert fulou_candidates[0]==Fulou.deserialize("peng,m1,m1+m1,null")
    assert fulou_candidates[1]==Fulou.deserialize("peng,m4,m4+m4,null")
    
    #チー
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m5","m9"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==1
    assert fulou_candidates[0]==Fulou.deserialize("chi,m3,m1+m2,null")
    
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m3","m4"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==7
    assert fulou_candidates[0]==Fulou.deserialize("chi,m1,m2+m3,null")
    assert fulou_candidates[1]==Fulou.deserialize("chi,m2,m1+m3,null")
    assert fulou_candidates[2]==Fulou.deserialize("chi,m2,m3+m4,null")
    assert fulou_candidates[3]==Fulou.deserialize("chi,m3,m1+m2,null")
    assert fulou_candidates[4]==Fulou.deserialize("chi,m3,m2+m4,null")
    assert fulou_candidates[5]==Fulou.deserialize("chi,m4,m2+m3,null")
    assert fulou_candidates[6]==Fulou.deserialize("chi,m5,m3+m4,null")
    
    #カン
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==2
    assert fulou_candidates[0]==Fulou.deserialize("minggang,m1,m1+m1+m1,null")
    assert fulou_candidates[1]==Fulou.deserialize("peng,m1,m1+m1,null")
    
    bingpai=[Pai.deserialize(s) for s in ["m1","m1","m1","m1"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==3
    assert fulou_candidates[0]==Fulou.deserialize("angang,null,m1+m1+m1+m1,null")
    assert fulou_candidates[1]==Fulou.deserialize("minggang,m1,m1+m1+m1,null")
    assert fulou_candidates[2]==Fulou.deserialize("peng,m1,m1+m1,null")
    
    bingpai=[Pai.deserialize(s) for s in ["m5","m5","m5","m5t"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==3
    assert fulou_candidates[0]==Fulou.deserialize("angang,null,m5+m5+m5+m5,null")
    assert fulou_candidates[1]==Fulou.deserialize("minggang,m5,m5+m5+m5,null")
    assert fulou_candidates[2]==Fulou.deserialize("peng,m5,m5+m5,null")
    
    #加槓
    bingpai=[Pai.deserialize(s) for s in ["z1"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia","peng,z4,z4+z4,shangjia"]]
    zimopai=Pai.deserialize("z2")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates)==2
    assert fulou_candidates[0]==Fulou.deserialize("jiagang,z1,z1+z1,null")
    assert fulou_candidates[1]==Fulou.deserialize("jiagang,z2,z2+z2,null")
    
    #暗槓+加槓
    bingpai=[Pai.deserialize(s) for s in ["m5","m5","m5","m5t"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=Pai.deserialize("z2")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates(fulou_type=["angang","jiagang"])
    assert len(fulou_candidates)==2
    assert fulou_candidates[0]==Fulou.deserialize("angang,null,m5+m5+m5+m5,null")
    assert fulou_candidates[1]==Fulou.deserialize("jiagang,z2,z2+z2,null")
    
    #ポン+チー
    bingpai=[Pai.deserialize(s) for s in ["m1","m2","m5","m5"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian","peng,z3,z3+z3,shangjia"]]
    zimopai=None
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates(fulou_type=["peng","chi","minggang"])
    assert len(fulou_candidates)==2
    assert fulou_candidates[0]==Fulou.deserialize("chi,m3,m1+m2,null")
    assert fulou_candidates[1]==Fulou.deserialize("peng,m5,m5+m5,null")
    
    #ポン+チー+カン
    bingpai=[Pai.deserialize(s) for s in ["m5","m5","m5","m5t","m7","m8","m9"]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian"]]
    zimopai=Pai.deserialize("z2")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates(fulou_type=["peng","chi","minggang"])
    assert len(fulou_candidates)==5+1+1
    
    #いろいろ
    bingpai = [Pai.deserialize(s) for s in ["m1","m2","m3","m4","m5","m6","m7","m8","m9","p1","p1","s2","s3",]]
    fulou=[Fulou.deserialize(s) for s in []]
    zimopai=Pai.deserialize("z7")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates) == 24

    bingpai = [Pai.deserialize(s) for s in ["m1","m1","m1","m2","m2","m3","m3",]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian",]]
    zimopai=Pai.deserialize("z7")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates) == 4+3+1
    
    bingpai = [Pai.deserialize(s) for s in ["m1","m2","m3","m4","m5","p1","p2",]]
    fulou=[Fulou.deserialize(s) for s in ["peng,z1,z1+z1,xiajia","peng,z2,z2+z2,duimian",]]
    zimopai=Pai.deserialize("z7")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates) == 11
    
    bingpai = [Pai.deserialize(s) for s in ["m1","m2","m3","m4","m5","m6","m7","m8","m9","p1","p1","s2","s3",]]
    fulou=[Fulou.deserialize(s) for s in []]
    zimopai=Pai.deserialize("z7")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates) == 24
    
    bingpai = [Pai.deserialize(s) for s in ["m1","m1","m1","m2","m3","m4","m5","m6","m7","m8","m9","m9","m9"]]
    fulou=[Fulou.deserialize(s) for s in []]
    zimopai=Pai.deserialize("z7")
    shoupai = Shoupai(bingpai=bingpai,fulou=fulou,zimopai=zimopai)
    fulou_candidates=shoupai._compute_fulou_candidates()
    assert len(fulou_candidates) == 25
    assert fulou_candidates[0]==Fulou.deserialize("chi,m1,m2+m3,null")
    assert fulou_candidates[1]==Fulou.deserialize("chi,m2,m1+m3,null")
    assert fulou_candidates[2]==Fulou.deserialize("chi,m2,m3+m4,null")
    assert fulou_candidates[3]==Fulou.deserialize("chi,m3,m1+m2,null")
    assert fulou_candidates[4]==Fulou.deserialize("chi,m3,m2+m4,null")
    assert fulou_candidates[5]==Fulou.deserialize("chi,m3,m4+m5,null")
    assert fulou_candidates[6]==Fulou.deserialize("chi,m4,m2+m3,null")
    assert fulou_candidates[7]==Fulou.deserialize("chi,m4,m3+m5,null")
    assert fulou_candidates[8]==Fulou.deserialize("chi,m4,m5+m6,null")
    assert fulou_candidates[9]==Fulou.deserialize("chi,m5,m3+m4,null")
    assert fulou_candidates[10]==Fulou.deserialize("chi,m5,m4+m6,null")
    assert fulou_candidates[11]==Fulou.deserialize("chi,m5,m6+m7,null")
    assert fulou_candidates[12]==Fulou.deserialize("chi,m6,m4+m5,null")
    assert fulou_candidates[13]==Fulou.deserialize("chi,m6,m5+m7,null")
    assert fulou_candidates[14]==Fulou.deserialize("chi,m6,m7+m8,null")
    assert fulou_candidates[15]==Fulou.deserialize("chi,m7,m5+m6,null")
    assert fulou_candidates[16]==Fulou.deserialize("chi,m7,m6+m8,null")
    assert fulou_candidates[17]==Fulou.deserialize("chi,m7,m8+m9,null")
    assert fulou_candidates[18]==Fulou.deserialize("chi,m8,m6+m7,null")
    assert fulou_candidates[19]==Fulou.deserialize("chi,m8,m7+m9,null")
    assert fulou_candidates[20]==Fulou.deserialize("chi,m9,m7+m8,null")
    assert fulou_candidates[21]==Fulou.deserialize("minggang,m1,m1+m1+m1,null")
    assert fulou_candidates[22]==Fulou.deserialize("minggang,m9,m9+m9+m9,null")
    assert fulou_candidates[23]==Fulou.deserialize("peng,m1,m1+m1,null")
    assert fulou_candidates[24]==Fulou.deserialize("peng,m9,m9+m9,null")

