from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional, Self
from .player import Player
from .pai import Pai
from .shan import Shan
from .wangpai import Wangpai
from .shoupai import Shoupai, Fulou, PatternResult
from .he import He
from .score import Score
from .rule import Rule
from .type import Feng, PlayerAction, Position
import random
from collections import Counter
from dataclasses import dataclass, field
from fastapi import WebSocket


@dataclass
class Hupai:
    name: List[str] = field(default_factory=list)
    fanshu: int = 0
    hu: int = 20
    pat: PatternResult = field(default_factory=lambda: PatternResult([], []))
    

class Game(BaseModel):
    players: List[Player] = Field(default=[Player() for _ in range(4)])
    shan: Shan = Field(default=Shan())
    wangpai: Wangpai = Field(default=Wangpai())
    rule: Rule = Field(default=Rule())
    score: Score = Field(default=Score())
    teban: Feng = Field(default="東")

    def qipai(self):
        # 数牌（赤ドラ以外）生成
        normal_pais = [
            Pai(suit=suit, num=num)
            for suit in ["m", "p", "s"]
            for num in range(1, 10)
            for _ in range(4)
        ]

        # 赤ドラ生成
        # red_pais = [Pai(suit=suit, num=5, is_red=True) for suit in ["m", "p", "s"]]
        red_pais = []

        # 字牌生成
        honor_pais = [Pai(suit="z", num=num) for num in range(1, 8) for _ in range(4)]

        # 全牌セット
        all_pais = normal_pais + red_pais + honor_pais
        random.shuffle(all_pais)

        # 王牌セット
        wangpai = [all_pais.pop() for _ in range(14)]
        self.wangpai = Wangpai(
            lingshangpai=wangpai[:4], baopai=wangpai[4:9], libaopai=wangpai[9:14]
        )
        # 通知用メッセージにドラ設定
        # self.score = Score(baopai=self.wangpai.get_baopai())
        self.score.baopai=self.wangpai.get_baopai()

        # 手牌セット
        for i in range(4):
            bingpai = sorted([all_pais.pop() for _ in range(13)],key=lambda x: (x.suit, x.num, x.is_red))
            self.players[i].shoupai = Shoupai(bingpai=bingpai)
            self.players[i].shoupai.do_qipai()
            self.players[i].he = He()
            

        # 山牌セット
        self.shan = Shan(pais=all_pais)

    def select_zuoci(self):
        random.shuffle(self.players)
        for i, f in enumerate(["東", "南", "西", "北"]):
            self.players[i].menfeng = f
            self.score.menfeng[i] = f
    
    def zimo(self, num: Literal[0, 1, 2, 3]):
        """
        Args:
            num (Literal[0, 1, 2, 3]):
                - 0: 起家
                - 1: 下家
                - 2: 対面
                - 3: 上家
        """
        zimopai = self.shan.pop()
        self.players[num].shoupai.do_zimo(zimopai)
        return zimopai

    def dapai(self, num: Literal[0, 1, 2, 3], dapai: Pai, dapai_idx: int):
        self.players[num].shoupai.do_dapai(dapai, dapai_idx)
        self.players[num].he.pais.append(dapai)
        hule_candidates = self.players[num].shoupai.hule_candidates
        fulou_candidates = self.players[num].shoupai.fulou_candidates

    def fulou(self, num: Literal[0, 1, 2, 3], fulou: Fulou):
        self.players[num].shoupai.do_fulou(fulou)
        # 一発消し
        for i in range(4):
            self.players[i].shoupai.is_yifa = False
    
    def get_last_recieved_fulou(self):
        fulou=None
        for i in range(4):
            if self.players[i].last_recieved_message and self.players[i].last_recieved_message.game.fulou:
                fulou=self.players[i].last_recieved_message.game.fulou
        
        if fulou is  None:
            raise ValueError(f"プレイヤーの副露情報が取得できません")
        return fulou
    
    
    def get_last_recieved_fulou_player(self):
        fulou_player_idx=None
        for i in range(4):
            if self.players[i].last_recieved_message and self.players[i].last_recieved_message.game.fulou:
                fulou_player_idx=i
        if fulou_player_idx is  None:
            raise ValueError(f"プレイヤーの副露情報が取得できません")
        return fulou_player_idx
    
    def lizhi(self, num: Literal[0, 1, 2, 3], dapai: Pai, dapai_idx: int):
        is_double_lizhi = (
            all(len(self.players[i].shoupai.fulou) == 0 for i in range(4))
            and len(self.players[num].he.pais) == 0
        )
        self.players[num].shoupai.do_lizhi(dapai, dapai_idx, is_double_lizhi)
        self.players[num].he.pais.append(dapai)
        hule_candidates = self.players[num].shoupai.hule_candidates
        fulou_candidates = self.players[num].shoupai.fulou_candidates

    def hule(
        self,
        num: Literal[0, 1, 2, 3],
        hulepai: Pai,
        option: List[Literal["qianggang", "lingshang"]] = [],
    ):
        best_hupai = Hupai()
        hulepats = self.players[num].shoupai.get_hulepattern(hulepai)
        for pat in hulepats:

            result_hupai = self._calculate_fanshu(num, pat, option)
            if result_hupai.fanshu > best_hupai.fanshu:
                best_hupai = result_hupai
        best_hupai=self._calculate_hu(num, best_hupai)
        defen=self._calcualate_defen(num,best_hupai)
        self.score.defen=[x + y for x, y in zip(self.score.defen, defen)]
        print("hule,best_hupai,num",best_hupai,num)
        return best_hupai
        
    def pingju(self):
        tingpai_ary=[self.players[i].shoupai.xiangting==0 for i in range(4)]
        pingju_defen=[0, 0, 0, 0]
        if all(tingpai_ary) or not any(tingpai_ary):
            return pingju_defen
        true_count = sum(tingpai_ary)
        false_count = len(tingpai_ary) - true_count
        
        # 1つの配分値を計算
        true_value = int(3000 / true_count)
        false_value = int(-true_value * true_count / false_count)
        
        # 結果の配列を作成
        pingju_defen= [true_value if x else false_value for x in tingpai_ary]
        self.score.defen=[x + y for x, y in zip(self.score.defen, pingju_defen)]
        return pingju_defen
        
        
    def _calcualate_defen(self,num: Literal[0, 1, 2, 3],hupai:Hupai):
        if hupai.fanshu==0:
            raise ValueError(f"役がありません.{hupai}")
        
        def get_manguan_defen():
            if hupai.fanshu<4:
                return 0
            if hupai.fanshu==4:
                if hupai.hu<40:
                    return 0
                else:
                    return 8000
            elif 4<hupai.fanshu<=5:
                return 8000
            elif 5<hupai.fanshu<=7:
                return 12000
            elif 7<hupai.fanshu<=10:
                return 16000
            elif 10<hupai.fanshu<=12:
                return 24000
            elif 12<hupai.fanshu:
                return 32000
            else:
                raise ValueError(f"役数が正しくありません.{hupai}")
        
        def is_parent(player_idx:int):
            return self.players[player_idx].menfeng=="東"
        
        def get_weight():
            weight=1.0
            #親なら1.5倍
            if is_parent(num):
                weight=1.5
            return weight
        
        def get_hule_defen():
            weight=get_weight()
            hule_defen=int(((32*hupai.hu*2**(hupai.fanshu-1)*weight +99) //100)*100)
            hule_defen= int(8000*weight) if hule_defen>int(8000*weight) else hule_defen
            return hule_defen
        
        def get_hule_type():
            hule_type= "zimo" if self.teban==self.players[num].menfeng else "rong"
            return hule_type
        
        def get_baojia_idx():
            for i in range(4):
                if self.teban==self.players[i].menfeng:
                    return i
            raise ValueError(f"放銃者が存在しません")
        
        #打点計算
        hule_defen=int(get_manguan_defen()*get_weight())
        if hule_defen==0:
            hule_defen=get_hule_defen()
        
        #打点配分
        defen=[0,0,0,0]
        if get_hule_type()=="rong": #ロンアガリ
            defen[num]=hule_defen
            defen[get_baojia_idx()]=-1*hule_defen
        else: #ツモアガリ
            if is_parent(num): #親
                child_defen=((hule_defen//3 +99) //100)*100
                defen[num]=child_defen*3
                for i in range(4):
                    if not is_parent(i):
                        defen[i]=-1*child_defen
                
            else: #子
                child_defen=((hule_defen//4 +99) //100)*100
                parent_defen=((hule_defen//2 +99) //100)*100
                defen[num]=child_defen*2+parent_defen
                for i in range(4):
                    if is_parent(i):
                        defen[i]=-1*parent_defen
                    else:
                        if i!=num:
                            defen[i]=-1*child_defen
        
        return defen

    def _calculate_hu(self, num: Literal[0, 1, 2, 3], hupai: Hupai):
        if "平和" in hupai.name and "門前清自摸和" in hupai.name:
            hupai.hu = 20
            return hupai
        elif "七対子" in hupai.name:
            hupai.hu = 25
            return hupai
        elif hupai.fanshu//100>0:
            hupai.hu = 20
            return hupai

        hu = 20
        anke_elem = [
            pais
            for pais in hupai.pat.get_pai_list()[:-1]
            + (
                [hupai.pat.get_pai_list()[-1]]
                if self.teban == self.players[num].menfeng
                else []
            )  # 自摸アガリであれば暗刻の可能性あり
            if len(pais) == 3 and pais[0] == pais[1]
        ]
        mingke_elem = [
            pais
            for pais in [
                f.get_pais()
                for f in self.players[num].shoupai.fulou
                if f.type == "peng"
            ]
            + (
                [hupai.pat.get_pai_list()[-1]]
                if self.teban != self.players[num].menfeng
                else []
            )  # ロンアガリであれば明刻の可能性あり
            if len(pais) == 3 and pais[0] == pais[1]
        ]
        angang_elem = [
            pais
            for pais in [
                f.get_pais()
                for f in self.players[num].shoupai.fulou
                if f.type == "angang"
            ]
        ]
        minggang_elem = [
            pais
            for pais in [
                f.get_pais()
                for f in self.players[num].shoupai.fulou
                if f.type in ["minggang", "jiagang"]
            ]
        ]

        #明刻、暗刻、明槓、暗槓
        for pais in anke_elem:
            if pais[0] in Pai.get_yaojiupai():
                hu += 8
            else:
                hu += 4

        for pais in mingke_elem:
            if pais[0] in Pai.get_yaojiupai():
                hu += 4
            else:
                hu += 2
        for pais in angang_elem:
            if pais[0] in Pai.get_yaojiupai():
                hu += 32
            else:
                hu += 16

        for pais in minggang_elem:
            if pais[0] in Pai.get_yaojiupai():
                hu += 16
            else:
                hu += 8

        #アガリ牌の待ち方
        tazi_elem = hupai.pat.get_pais_by_num(len(hupai.pat.nums) - 1)
        if (
            len(tazi_elem) == 2
            or (tazi_elem[0].num == 1 and tazi_elem[1].num == 2)
            or (tazi_elem[0].num == 8 and tazi_elem[1].num == 9)
            or (tazi_elem[1].num - tazi_elem[0].num == 2)
        ):
            hu += 2
        
        #雀頭
        jiangpai = (
            tazi_elem
            if len(tazi_elem) == 2
            else hupai.pat.get_pais_by_num(len(hupai.pat.nums) - 2)
        )
        if jiangpai[0].get_name() in [
            "白",
            "發",
            "中",
            self.score.zhuangfeng,
            self.players[num].menfeng,
        ]:
            hu += 2
        
        #自摸orロン
        if self.teban == self.players[num].menfeng:
            hu += 2
        else:
            #メンゼンロン
            if all(f.type=="angang" for f in self.players[num].shoupai.fulou):
                hu += 10

        #切り上げ
        hu = ((hu - 1) // 10 + 1) * 10
        hupai.hu = hu

        return hupai

    def _calculate_fanshu(
        self,
        num: Literal[0, 1, 2, 3],
        pat: PatternResult,
        option: List[Literal["qianggang", "lingshang"]] = [],
    ):
        hupai = Hupai(pat=pat)

        # 七対子
        if Counter(pat.nums)[2] == 7:
            hupai.fanshu += 2
            hupai.name.append("七対子")

        # リーチ：lizhi
        if self.players[num].shoupai.lizhi_flag == 1:
            hupai.fanshu += 1
            hupai.name.append("立直")
        elif self.players[num].shoupai.lizhi_flag == 2:
            hupai.fanshu += 2
            hupai.name.append("ダブル立直")

        # 一発
        if self.players[num].shoupai.lizhi_flag and self.players[num].shoupai.is_yifa:
            hupai.fanshu += 1
            hupai.name.append("一発")

        # ツモ：zimo
        if (
            all(f.type == "angang" for f in self.players[num].shoupai.fulou)
            and self.teban == self.players[num].menfeng
        ):
            hupai.fanshu += 1
            hupai.name.append("門前清自摸和")

        # 風牌
        if any(
            p.suit == "z"
            and (
                (p.num == 1 and self.players[num].menfeng == "東")
                or (p.num == 2 and self.players[num].menfeng == "南")
                or (p.num == 3 and self.players[num].menfeng == "西")
                or (p.num == 4 and self.players[num].menfeng == "北")
            )
            for p in [
                pais[0] for pais in pat.get_pai_list() if len(pais) == 3
            ]  # 手牌に自風牌暗刻があるか確認
            + [
                f.menpais[0] for f in self.players[num].shoupai.fulou
            ]  # 副露に自風牌副露があるか確認
        ):
            hupai.fanshu += 1
            hupai.name.append(f"自風 {self.players[num].menfeng}")

        # 場風
        if any(
            p.suit == "z"
            and (
                (p.num == 1 and self.score.zhuangfeng == "東")
                or (p.num == 2 and self.score.zhuangfeng == "南")
                or (p.num == 3 and self.score.zhuangfeng == "西")
                or (p.num == 4 and self.score.zhuangfeng == "北")
            )
            for p in [
                pais[0] for pais in pat.get_pai_list() if len(pais) == 3
            ]  # 手牌に自風牌暗刻があるか確認
            + [
                f.menpais[0] for f in self.players[num].shoupai.fulou
            ]  # 副露に自風牌副露があるか確認
        ):
            hupai.fanshu += 1
            hupai.name.append(f"場風 {self.score.zhuangfeng}")

        # 役牌：sanyuanpai
        sanyuanpai = [
            p
            for p in [pais[0] for pais in pat.get_pai_list() if len(pais) == 3]  # 手牌
            + [f.menpais[0] for f in self.players[num].shoupai.fulou]  # 副露
            if p.suit == "z" and p.num in [5, 6, 7]
        ]
        for p in sanyuanpai:
            hupai.fanshu += 1
            if p.num == 5:
                hupai.name.append(f"翻牌 白")
            elif p.num == 6:
                hupai.name.append(f"翻牌 發")
            else:
                hupai.name.append(f"翻牌 中")

        # タンヤオ：tanyao
        if all(
            p in Pai.get_zhongzhangpai()
            for p in [p for p in self.players[num].shoupai.get_fuloupais()] + pat.pais
        ):

            hupai.fanshu += 1
            hupai.name.append(f"断幺九")

        # 平和：pinghu
        if (
            Counter(pat.nums)[3] == 4  # 手牌の面子が4つ
            and all(
                pais[0].num != pais[1].num
                for pais in pat.get_pai_list()
                if len(pais) == 3
            )  # 面子が全て順子
            and (
                pat.nums[-1] == 3
                and 2 <= pat.pais[-3].num <= 7
                and pat.pais[-3].num + 1 == pat.pais[-2].num
            )  # 両面待ち
            and (
                pat.get_pais_by_num(len(pat.nums) - 2)[0].get_name()
                not in [
                    "白",
                    "發",
                    "中",
                    self.score.zhuangfeng,
                    self.players[num].menfeng,
                ]
            ) #雀頭が役牌でない
        ):
            hupai.fanshu += 1
            hupai.name.append(f"平和")

        # 一盃口：beikou
        # print("beikou",[sorted(pais,key=lambda x:x.serialize()) for j,pais in enumerate(pat.get_pai_list())],pat.nums)
        if all(  # 副露は暗槓のみ可
            f.type == "angang" for f in self.players[num].shoupai.fulou
        ) and sum(
            sorted(pais, key=lambda x: x.serialize())
            in [
                sorted(pais, key=lambda x: x.serialize())
                for j, pais in enumerate(pat.get_pai_list())
                if i != j
            ]
            for (i, pais) in enumerate(pat.get_pai_list())
            if len(pais) == 3
        ) in [
            2,
            3,
        ]:
            hupai.fanshu += 1
            hupai.name.append(f"一盃口")

        # 海底撈月
        if len(self.shan.pais) == 0 and self.teban == self.players[num].menfeng:
            hupai.fanshu += 1
            hupai.name.append(f"海底撈月")

        # 河底撈魚
        if len(self.shan.pais) == 0 and self.teban != self.players[num].menfeng:
            hupai.fanshu += 1
            hupai.name.append(f"河底撈魚")

        # チャンカン:qianggang
        if "qianggang" in option:
            hupai.fanshu += 1
            hupai.name.append(f"槍槓")

        # 嶺上開花
        if "lingshang" in option:
            hupai.fanshu += 1
            hupai.name.append(f"嶺上開花")

        # 三色同順sansetongshun
        sansetongshun_elem1: List[Pai] = [
            sorted(pais, key=lambda x: x.serialize())[0]
            for pais in pat.get_pai_list()
            if len(pais) == 3
            and pais[0].suit in ["m", "p", "s"]
            and pais[0].num != pais[1].num
        ]
        sansetongshun_elem2: List[Pai] = [
            sorted([f.nakipai, *f.menpais], key=lambda x: (x.num))[0]
            for f in self.players[num].shoupai.fulou
            if f.type == "chi"
        ]
        # print("sansetongshun_elem1,sansetongshun_elem2",sansetongshun_elem1,sansetongshun_elem2)
        ##メンゼン
        if len(sansetongshun_elem1) >= 3 and any(  # 手牌面子3組以上
            all(
                f"{s}{p.num}" in [p.serialize()[:2] for p in sansetongshun_elem1]
                for s in ["m", "p", "s"]
            )
            for p in sansetongshun_elem1
        ):  # 萬子、筒子、索子の同じ順子が手牌に存在すること
            hupai.fanshu += 2
            hupai.name.append(f"三色同順")
        ##食い下がり
        elif len(sansetongshun_elem1) + len(sansetongshun_elem2) >= 3 and any(
            all(
                f"{s}{p.num}"
                in [
                    p.serialize()[:2] for p in sansetongshun_elem1 + sansetongshun_elem2
                ]
                for s in ["m", "p", "s"]
            )
            for p in sansetongshun_elem1 + sansetongshun_elem2
        ):  # 萬子、筒子、索子の同じ順子が手牌+副露に存在すること
            hupai.fanshu += 1
            hupai.name.append(f"三色同順")

        # 一気通貫yiqitongguan
        ##メンゼン
        if len(sansetongshun_elem1) >= 3 and any(  # 手牌面子3組以上
            all(
                f"{s}{n}" in [p.serialize()[:2] for p in sansetongshun_elem1]
                for n in ["1", "4", "7"]
            )
            for s in ["m", "p", "s"]
        ):
            hupai.fanshu += 2
            hupai.name.append(f"一気通貫")
        ##食い下がり
        elif len(
            sansetongshun_elem1 + sansetongshun_elem2
        ) >= 3 and any(  # 手牌面子3組以上
            all(
                f"{s}{n}"
                in [
                    p.serialize()[:2] for p in sansetongshun_elem1 + sansetongshun_elem2
                ]
                for n in ["1", "4", "7"]
            )
            for s in ["m", "p", "s"]
        ):
            hupai.fanshu += 1
            hupai.name.append(f"一気通貫")

        # ホンイツhunyise
        hunyise_elem1 = [p.suit for p in pat.pais]
        hunyise_elem2 = [f.menpais[0].suit for f in self.players[num].shoupai.fulou]
        if any(
            Counter(hunyise_elem1 + hunyise_elem2)[s] > 0
            and Counter(hunyise_elem1 + hunyise_elem2)["z"] > 0  # 字牌と数牌が1牌以上
            and Counter(hunyise_elem1 + hunyise_elem2)[s]
            + Counter(hunyise_elem1 + hunyise_elem2)["z"]  # 字牌+数牌=手牌の数＋副露数
            == len(hunyise_elem1) + len(hunyise_elem2)
            for s in ["m", "p", "s"]
        ):
            ##メンゼン
            if all(
                f.type == "angang" for f in self.players[num].shoupai.fulou
            ):  # 全て暗槓または副露なし
                hupai.fanshu += 3
                hupai.name.append(f"混一色")
            ##食い下がり
            else:
                hupai.fanshu += 2
                hupai.name.append(f"混一色")

        # 対々和duiduihu
        if (
            all(pais[0] == pais[1] for pais in pat.get_pai_list() if len(pais) == 3)
            and all(f.type != "chi" for f in self.players[num].shoupai.fulou)
            and Counter(pat.nums)[2] == 1
        ):
            hupai.fanshu += 2
            hupai.name.append(f"対々和")

        # 三暗刻
        anke_elem = [
            pais
            for pais in pat.get_pai_list()[:-1]
            + (
                [pat.get_pai_list()[-1]]
                if self.teban == self.players[num].menfeng
                else []
            )  # 自摸アガリであれば暗刻の可能性あり
            if len(pais) == 3 and pais[0] == pais[1]
        ]
        if len(anke_elem) == 3:
            hupai.fanshu += 2
            hupai.name.append(f"三暗刻")

        # 三色同刻sansetongke
        sansetongke_elem1: List[Pai] = [
            pais[0]
            for pais in pat.get_pai_list()
            if len(pais) == 3 and pais[0].suit in ["m", "p", "s"] and pais[0] == pais[1]
        ]
        sansetongke_elem2: List[Pai] = [
            f.menpais[0]
            for f in self.players[num].shoupai.fulou
            if f.menpais[0] == f.menpais[1]
        ]
        if any(
            all(
                f"{s}{p.num}"
                in [p.serialize()[:2] for p in sansetongke_elem1 + sansetongke_elem2]
                for s in ["m", "p", "s"]
            )
            for p in sansetongke_elem1 + sansetongke_elem2
        ):  # 萬子、筒子、索子の同じ刻子が手牌に存在すること
            hupai.fanshu += 2
            hupai.name.append(f"三色同刻")

        # 混老頭
        hunlaotou_elem = [f.menpais[0] for f in self.players[num].shoupai.fulou]
        if (
            all(f.type != "chi" for f in self.players[num].shoupai.fulou)
            and any(
                p.serialize()[:2] in ["m1", "m9", "p1", "p9", "s1", "s9"]
                for p in pat.pais + hunlaotou_elem
            )
            and any(
                p.serialize()[:2] in [f"z{n}" for n in range(1, 8)]
                for p in pat.pais + hunlaotou_elem
            )
            and all(
                p.serialize()[:2]
                in ["m1", "m9", "p1", "p9", "s1", "s9"] + [f"z{n}" for n in range(1, 8)]
                for p in pat.pais + hunlaotou_elem
            )
        ):
            hupai.fanshu += 2
            hupai.name.append(f"混老頭")

        # チャンタhunquandaiyaojiu
        hunquandaiyaojiu_elem1 = [
            sorted(pais, key=lambda x: x.serialize())
            for pais in pat.get_pai_list()
            if len(pais) != 1
        ]
        hunquandaiyaojiu_elem2 = [
            sorted(
                f.get_pais(),
                key=lambda x: x.serialize(),
            )
            for f in self.players[num].shoupai.fulou
        ]
        # print("hunquandaiyaojiu_elem1+hunquandaiyaojiu_elem2",hunquandaiyaojiu_elem1+hunquandaiyaojiu_elem2)
        ##メンゼン
        if (
            any(  # 少なくとも1つの辺帳面子を含む
                pais[0] != pais[1]
                and pais[0].serialize()[:2] in ["m1", "m7", "p1", "p7", "s1", "s7"]
                for pais in hunquandaiyaojiu_elem1 + hunquandaiyaojiu_elem2
            )
            and any(  # 少なくとも1つの字牌を含む
                pais[0].suit == "z"
                for pais in hunquandaiyaojiu_elem1 + hunquandaiyaojiu_elem2
            )
            and all(  # 全てにヤオチュー牌が含まれる
                any(p in Pai.get_yaojiupai() for p in pais)
                for pais in hunquandaiyaojiu_elem1 + hunquandaiyaojiu_elem2
            )
        ):
            ##メンゼン
            if all(
                f.type == "angang" for f in self.players[num].shoupai.fulou
            ):  # 全て暗槓または副露なし
                hupai.fanshu += 2
                hupai.name.append(f"混全帯幺九")
            ##食い下がり
            else:
                hupai.fanshu += 1
                hupai.name.append(f"混全帯幺九")

        # 小三元
        if sum(
            Counter(pat.pais + [p for p in self.players[num].shoupai.get_fuloupais()])[
                Pai.deserialize(s)
            ]
            >= 3
            for s in ["z5", "z6", "z7"]
        ) == 2 and any(  # 役牌3枚以上が2つ
            Counter(pat.pais)[Pai.deserialize(s)] == 2 for s in ["z5", "z6", "z7"]
        ):  # 役牌のいずれかが雀頭
            hupai.fanshu += 2
            hupai.name.append(f"小三元")

        # 三槓子
        if (
            len(
                [
                    f
                    for f in self.players[num].shoupai.fulou
                    if f.type in ["angang", "jiagang", "minggang"]
                ]
            )
            == 3
        ):
            hupai.fanshu += 2
            hupai.name.append(f"三槓子")

        # 純全帯幺九
        if any(  # 少なくとも1つの辺帳面子を含む
            pais[0] != pais[1]
            and pais[0].serialize()[:2] in ["m1", "m7", "p1", "p7", "s1", "s7"]
            for pais in hunquandaiyaojiu_elem1 + hunquandaiyaojiu_elem2
        ) and all(  # 全てに一九牌が含まれる
            any(
                p in [Pai.deserialize(s) for s in ["m1", "m9", "p1", "p9", "s1", "s9"]]
                for p in pais
            )
            for pais in hunquandaiyaojiu_elem1 + hunquandaiyaojiu_elem2
        ):
            ##メンゼン
            if all(
                f.type == "angang" for f in self.players[num].shoupai.fulou
            ):  # 全て暗槓または副露なし
                hupai.fanshu += 3
                hupai.name.append(f"純全帯幺九")
            ##食い下がり
            else:
                hupai.fanshu += 2
                hupai.name.append(f"純全帯幺九")

        # 二盃口
        if (
            sum(
                sorted(pais, key=lambda x: x.serialize())
                in [
                    sorted(pais, key=lambda x: x.serialize())
                    for j, pais in enumerate(pat.get_pai_list())
                    if i != j
                ]
                for (i, pais) in enumerate(pat.get_pai_list())
                if len(pais) == 3
            )
            == 4
        ):
            hupai.fanshu += 3
            hupai.name.append(f"二盃口")

        # 清一色qingyise
        hunyise_elem1 = [p.suit for p in pat.pais]
        hunyise_elem2 = [f.menpais[0].suit for f in self.players[num].shoupai.fulou]
        if any(
            Counter(hunyise_elem1 + hunyise_elem2)[s]
            == len(hunyise_elem1) + len(hunyise_elem2)  # 数牌=手牌の数＋副露数
            for s in ["m", "p", "s"]
        ):
            ##メンゼン
            if all(
                f.type == "angang" for f in self.players[num].shoupai.fulou
            ):  # 全て暗槓または副露なし
                hupai.fanshu += 6
                hupai.name.append(f"清一色")
            ##食い下がり
            else:
                hupai.fanshu += 5
                hupai.name.append(f"清一色")

        # 流し満貫

        # 天和
        if (
            all(
                len(self.players[i].shoupai.fulou) == 0
                and len(self.players[i].he.pais) == 0
                for i in range(4)
            )
            and self.players[num].menfeng == "東"
            and self.teban == "東"
        ):
            hupai.fanshu += 100
            hupai.name.append(f"天和")

        # 地和
        if (
            all(len(self.players[i].shoupai.fulou) == 0 for i in range(4))
            and len(self.players[num].he.pais) == 0
            and self.players[num].menfeng != "東"
            and self.players[num].menfeng == self.teban
        ):
            hupai.fanshu += 100
            hupai.name.append(f"地和")

        # 人和

        # 国士無双
        if Counter(pat.nums)[1] == 14:
            hupai.fanshu += 100
            hupai.name.append("国士無双")

        # 緑一色
        if all(
            p.serialize()[:2] in ["s2", "s3", "s4", "s6", "s8", "z6"]
            for p in [p for p in self.players[num].shoupai.get_fuloupais()] + pat.pais
        ):
            hupai.fanshu += 100
            hupai.name.append(f"緑一色")

        # 大三元
        if all(
            Counter([p for p in self.players[num].shoupai.get_fuloupais()] + pat.pais)[
                Pai.deserialize(s)
            ]
            >= 3
            for s in ["z5", "z6", "z7"]
        ):
            hupai.fanshu += 100
            hupai.name.append(f"大三元")

        # 小四喜
        if sum(
            Counter(pat.pais + [p for p in self.players[num].shoupai.get_fuloupais()])[
                Pai.deserialize(s)
            ]
            >= 3
            for s in ["z1", "z2", "z3", "z4"]
        ) == 3 and any(  # 風牌3枚以上が3つ
            Counter(pat.pais)[Pai.deserialize(s)] == 2 for s in ["z1", "z2", "z3", "z4"]
        ):  # 風牌のいずれかが雀頭
            hupai.fanshu += 100
            hupai.name.append(f"小四喜")

        # 字一色
        if all(
            p.serialize()[:2] in [f"z{n}" for n in range(1, 8)]
            for p in [p for p in self.players[num].shoupai.get_fuloupais()] + pat.pais
        ):
            hupai.fanshu += 100
            hupai.name.append(f"字一色")

        # 九蓮宝燈
        if any(
            Counter([p.suit for p in pat.pais])[s] == 14
            and all(Counter([p.num for p in pat.pais])[n] >= 1 for n in range(2, 9))
            and all(Counter([p.num for p in pat.pais])[n] >= 3 for n in [1, 9])
            for s in ["m", "p", "s"]
        ):
            hupai.fanshu += 100
            hupai.name.append(f"九蓮宝燈")

        # 四暗刻
        if len(anke_elem) == 4:
            hupai.fanshu += 100
            hupai.name.append(f"四暗刻")

        # 清老頭
        if all(
            p.serialize()[:2] in ["m1", "m9", "p1", "p9", "s1", "s9"]
            for p in [p for p in self.players[num].shoupai.get_fuloupais()] + pat.pais
        ):
            hupai.fanshu += 100
            hupai.name.append(f"清老頭")

        # 四槓子
        if (
            len(
                [
                    f
                    for f in self.players[num].shoupai.fulou
                    if f.type in ["angang", "jiagang", "minggang"]
                ]
            )
            == 4
        ):
            hupai.fanshu += 100
            hupai.name.append(f"四槓子")

        # 四暗刻単騎

        # 大四喜
        if (
            sum(
                Counter(
                    pat.pais + [p for p in self.players[num].shoupai.get_fuloupais()]
                )[Pai.deserialize(s)]
                >= 3
                for s in ["z1", "z2", "z3", "z4"]
            )
            == 4
        ):
            hupai.fanshu += 100
            hupai.name.append(f"大四喜")

        return hupai

    def get_turn(self, num: Literal[0, 1, 2, 3]) -> Position:
        if self.players[num].menfeng == self.teban:
            return "main"

        position_map = {
            "東": {"南": "xiajia", "西": "duimian", "北": "shangjia"},
            "南": {"東": "shangjia", "西": "xiajia", "北": "duimian"},
            "西": {"東": "duimian", "南": "shangjia", "北": "xiajia"},
            "北": {"東": "xiajia", "南": "duimian", "西": "shangjia"},
        }

        return position_map[self.players[num].menfeng][self.teban]

    def next_teban(self):
        if self.teban == "東":
            self.teban = "南"
        elif self.teban == "南":
            self.teban = "西"
        elif self.teban == "西":
            self.teban = "北"
        else:
            self.teban = "東"
        return self.teban
    
    def get_next_feng(self,feng:Feng):
        feng_list:List[Feng]=["東", "北", "西", "南"]
        feng_idx=feng_list.index(feng)
        return feng_list[feng_idx+1] if 0<=feng_idx<3 else "東"
    
    def next_game(self):
        players=[p.model_copy() for p in self.players]
        for p in players:
            p.menfeng=self.get_next_feng(p.menfeng)
            p.shoupai=Shoupai()
        shan=Shan()
        wangpai=Wangpai()
        rule=self.rule.model_copy()
        score=Score()
        score.defen=self.score.defen
        score.jushu=self.score.jushu+1
        score.zhuangfeng=score.get_zhuangfeng()
        for i in range(4):
            score.menfeng[i]=self.get_next_feng(self.score.menfeng[i])
        teban="東"
        return Game(players=players,shan=shan,wangpai=wangpai,rule=rule,score=score,teban=teban)
    
    def get_player(self,websocket:WebSocket):
        player:Optional[Player]=None
        for i in range(4):
            if self.players[i].socket==websocket:
                player=self.players[i]
        
        if player is None:
            raise ValueError("指定したプレイヤーは存在しません")
        
        return player