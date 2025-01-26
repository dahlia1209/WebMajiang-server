from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional, NamedTuple
from .pai import Pai
from collections import defaultdict
from .type import Feng, PlayerAction, Position, Combination
from collections import Counter
from dataclasses import dataclass, field
from copy import deepcopy
import warnings

FulouType = Literal["chi", "peng", "minggang", "angang", "jiagang"]


@dataclass
class PatternResult:
    pais: List[Pai]
    nums: List[int]

    def get_pais_by_num(self, num: int):
        return self.pais[sum(self.nums[:num]) : sum(self.nums[:num]) + self.nums[num]]

    def get_pai_list(self):
        return [
            self.pais[sum(self.nums[:i]) : sum(self.nums[:i]) + n]
            for i, n in enumerate(self.nums)
        ]
        
@dataclass
class XiangtingResult:
    xiangting: int = 99
    best_candidates: List[PatternResult] = field(default_factory=list)
    hule_candidates: List[PatternResult] = field(default_factory=list)


class Fulou(BaseModel):
    type: FulouType
    fuloupai: Optional[Pai] = Field(default=None)
    menpais: List[Pai] = Field(default=[])
    position: Optional[Position] = Field(default=None)

    def serialize(self, without_red: bool = False) -> str:
        point = 2 if without_red else 3
        ns = self.fuloupai.serialize()[:point] if self.fuloupai else "null"
        fs = (
            "+".join(p.serialize()[:point] for p in self.menpais)
            if self.menpais
            else "null"
        )
        ps = self.position if self.position else "null"
        s = ",".join([str(self.type), ns, fs, ps])
        return s

    def get_without_red(self):
        return Fulou(
            type=self.type,
            fuloupai=(
                Pai(suit=self.fuloupai.suit, num=self.fuloupai.num)
                if self.fuloupai
                else None
            ),
            menpais=[Pai(suit=p.suit, num=p.num) for p in self.menpais],
            position=self.position,
        )

    def get_pais(self):
        return [p for p in ([self.fuloupai] if self.fuloupai else []) + self.menpais]

    @staticmethod
    def deserialize(s: str) -> "Fulou":
        ss = s.split(",")
        if len(ss) != 4:
            raise ValueError(f"指定した文字列に誤りがあります:{s}")

        t = ss[0]  # FulouType
        n = None if ss[1] == "null" else Pai.deserialize(ss[1])
        f = [] if ss[2] == "null" else [Pai.deserialize(fs) for fs in ss[2].split("+")]
        p = None if ss[3] == "null" else ss[3]

        return Fulou(type=t, fuloupai=n, menpais=f, position=p)


class Shoupai(BaseModel):
    bingpai: List[Pai] = Field(default=[])
    fulou: List[Fulou] = Field(default=[])
    zimopai: Optional[Pai] = Field(default=None)
    hule_candidates: List[PatternResult] = Field(default=[])
    fulou_candidates: List[Fulou] = Field(default=[])
    # lizhi_candidates: List[Fulou] = Field(default=[])
    lizhi_pai: List[Pai] = Field(default=[])
    xiangting: int = Field(default=99)
    bingpai_candidates: List[PatternResult] = Field(default=[])
    lizhi_flag: int = Field(default=0)
    is_yifa: bool = Field(default=False)

    def do_qipai(self):
        # シャン点数計算
        self._compute_xiangting()
    
    def do_zimo(self, pai: Pai):
        if self.zimopai is not None:
            raise ValueError(f"ツモ牌がすでに存在します.zimopai:{self.zimopai}")
        self.zimopai = pai

        # アガリ形の確認
        # self._check_hule()

        # リーチ候補探索
        self._comupute_lizhi_candidates()

        # 副露候補候補
        self._compute_fulou_candidates(fulou_type=["angang", "jiagang"])

    def do_dapai(self, dapai: Pai, dapai_idx: int):
        self._check_dapai(dapai, dapai_idx)

        dapai: Pai
        if 0 <= dapai_idx < len(self.bingpai):
            dapai = self.bingpai.pop(dapai_idx)
        elif dapai_idx == 99:
            dapai = self.zimopai
            self.zimopai = None

        # ツモ牌を手牌に加えてソート
        sorted_pais = sorted(
            self._get_bingpai(),
            key=lambda x: (x.suit, x.num, x.is_red),
        )
        self.zimopai = None
        self.bingpai = sorted_pais

        # 副露候補候補
        self._compute_fulou_candidates(fulou_type=["chi", "peng", "minggang"])

        # シャン点数計算
        self._compute_xiangting()

        # 一発は消える
        self.is_yifa = False

        return dapai
    
    def _get_bingpai(self):
        return sorted(self.bingpai + ([self.zimopai] if self.zimopai else []),key=lambda x: (x.suit, x.num, x.is_red))

    def _validate_fulou(self, fulou: Fulou):
        fulou_without_red = fulou.get_without_red()
        if (
            fulou_without_red.model_copy(update={"position": None})
            not in self.fulou_candidates
        ):
            raise ValueError(
                f"指定された副露はできません。指定された副露{fulou.serialize()}.副露候補:{[f.serialize() for f in self.fulou_candidates]}"
            )

        if fulou_without_red.type in ["chi", "peng", "minggang"] and not fulou.position:
            raise ValueError(
                f"副露の鳴き先が指定されていません.副露:{fulou.serialize()}."
            )
            
        
        return fulou
    
    def _process_jiagang(self, fulou: Fulou):
        if not fulou.fuloupai:
            raise ValueError(f"加槓の副露牌が指定されていません,fulou:{fulou.serialize()}")
        fulou_id,peng=next((i,f) for i,f in enumerate(self.fulou) if fulou.fuloupai==f.fuloupai and f.type=="peng") 
        jiagang = peng.model_copy(update={"type": "jiagang"})
        jiagangpai=next(p for p in self._get_bingpai() if p.serialize(2)==fulou.fuloupai.serialize(2))
        jiagang.menpais.append(jiagangpai)
        bingpai=[p for p in self._get_bingpai() if p.serialize(2)!=fulou.fuloupai.serialize(2)]
        self.fulou[fulou_id]=jiagang
        self.bingpai = sorted(bingpai, key=lambda x: (x.suit, x.num, x.is_red))
        self.zimopai = None    
        
    def _get_removed_bingpai(self,tar:List[Pai]):
        pais_str=[p.serialize() for p in self._get_bingpai()]
        tar_str=[p.serialize() for p in tar]
        for ts in tar_str:
            del pais_str[next(i for i,ps in enumerate(pais_str) if ps==ts)]
        return [Pai.deserialize(ps) for ps in pais_str]
    
    def _process_fulou_common(self, fulou: Fulou):
        self.bingpai = self._get_removed_bingpai(fulou.menpais)
        self.zimopai = None
        self.fulou.append(fulou)
    
    def do_fulou(self, fulou: Fulou):
        """副露（チー、ポン、明槓、暗槓、加槓）を実行する汎用関数"""
        fulou=self._validate_fulou(fulou)
        processes = {
            "jiagang": self._process_jiagang,
            "angang": self._process_fulou_common,
            "chi": self._process_fulou_common,
            "minggang": self._process_fulou_common,
            "peng": self._process_fulou_common,
        }
        
        process=processes.get(fulou.type)
        if not process:
            raise ValueError(f"副露の種類が正しくありません。指定された副露：{fulou.type}")
        process(fulou)
        
        if fulou.type in ["chi", "peng"]:
            # 副露候補探索
            self._compute_fulou_candidates(fulou_type=["angang", "jiagang"])

    def do_hule(self):
        pass

    def _check_dapai(self, dapai: Pai, dapai_idx: int):
        if 0 <= dapai_idx < len(self.bingpai):
            if self.bingpai[dapai_idx] != dapai:
                raise ValueError(
                    f"牌番号と打牌が一致していません.牌番号:{dapai_idx},牌番号の手牌:{self.bingpai[dapai_idx]},打牌:{dapai}"
                )
            if self.lizhi_flag:
                raise ValueError(f"リーチ中に手牌から打牌しています")
        elif dapai_idx == 99:
            if self.zimopai.serialize() != dapai.serialize():
                raise ValueError(
                    f"ツモ牌と打牌が一致していません.牌番号:{dapai_idx},ツモ牌:{self.zimopai},打牌:{dapai}"
                )
        else:
            raise ValueError(
                f"指定したインデックスは正しくありません.idx={dapai_idx},手牌数={len(self.bingpai)}"
            )
        return True

    def do_lizhi(self, dapai: Pai, dapai_idx: int,is_double_lizhi:bool=False):
        self.do_dapai(dapai, dapai_idx)

        # リーチフラグ
        self.lizhi_flag = 1 if not is_double_lizhi else 2
        self.is_yifa = True

        # アガリ系探索
        # self._compute_xiangting()

        return dapai

    def get_hulepattern(self, hulepai: Pai):
        hulepattern = [
            pat
            for pat in self.hule_candidates
            if pat.pais[-1].serialize(2) == hulepai.serialize(2)
        ]
        if not hulepattern:
            raise ValueError(
                f"アガリ形がありません.手牌:{self.bingpai}. アガリ牌:{hulepai}"
            )
        return hulepattern

    def _compute_fulou_candidates(
        self,
        fulou_type: List[FulouType] = ["chi", "peng", "minggang", "angang", "jiagang"],
        combination_list: Dict[Combination, List[str]] = {},
    ):
        fulou_candidates: List[Fulou] = []
        if not combination_list:
            combination_list = self._find_pai_combinations(self.bingpai)

        # チー候補
        for pai_str in combination_list["tazi"]:
            if "chi" not in fulou_type:
                break
            t1, t2 = [Pai.deserialize(s) for s in pai_str.split("+")]
            li = [
                Pai(suit=t1.suit, num=t1.num + n)
                for n in [-1, 1, 2]
                if t1.num + n in range(1, 10)
            ]
            for x in li:
                if sorted([x.num] + [t1.num, t2.num]) in [
                    [t1.num - 1, t1.num, t1.num + 1],
                    [t1.num, t1.num + 1, t1.num + 2],
                ]:
                    fulou_candidates.append(
                        Fulou(type="chi", fuloupai=x, menpais=[t1, t2])
                    )

        # ポン候補
        for pai_str in combination_list["duizi"]:
            if "peng" not in fulou_type:
                break
            p1, p2 = [Pai.deserialize(s) for s in pai_str.split("+")]
            fulou_candidates.append(Fulou(type="peng", fuloupai=p1, menpais=[p1, p2]))

        # 明槓候補
        for pai_str in combination_list["kezi"]:
            if "minggang" not in fulou_type:
                break
            m1, m2, m3 = [Pai.deserialize(s) for s in pai_str.split("+")]
            fulou_candidates.append(
                Fulou(type="minggang", fuloupai=m1, menpais=[m1, m2, m3])
            )

        # 暗槓候補
        for pai_str in combination_list["kezi"]:
            if "angang" not in fulou_type:
                break
            m1, m2, m3 = [Pai.deserialize(s) for s in pai_str.split("+")]
            if self.zimopai and self.zimopai.serialize(2) == m1.serialize(2):
                fulou_candidates.append(Fulou(type="angang", menpais=[m1, m2, m3, m1]))
        for pai_str in combination_list["gangzi"]:
            if "angang" not in fulou_type:
                break
            a1, a2, a3, a4 = [Pai.deserialize(s) for s in pai_str.split("+")]
            fulou_candidates.append(Fulou(type="angang", menpais=[a1, a2, a3, a4]))

        # 加槓候補
        for f in self.fulou:
            if "jiagang" not in fulou_type:
                break
            if f.type == "peng" and f.fuloupai.serialize(2) in [
                p.serialize(2)
                for p in self._get_bingpai()
            ]:
                fulou_candidates.append(
                    Fulou(type="jiagang", fuloupai=f.fuloupai, menpais=f.menpais)
                )

        self.fulou_candidates = sorted(
            fulou_candidates,
            key=lambda x: (
                x.type,
                x.fuloupai.serialize() if x.fuloupai else x.fuloupai,
                x.menpais[0].serialize() if x.menpais else None,
            ),
        )

        return self.fulou_candidates

    def _get_unique_pais(self, pais: List[Pai]):
        sorted_bingpai = sorted(pais, key=lambda x: (x.suit, x.num, x.is_red))
        unique_pais = [
            p
            for (i, p) in enumerate(sorted_bingpai)
            if i == 0 or p != sorted_bingpai[i - 1]
        ]
        return unique_pais

    # 国士無双シャン点数取得
    def _get_kokushi_xiangting(self, pais: List[Pai] = []):
        result = XiangtingResult()
        if not pais:
            pais = self.bingpai
        if len(pais) < 13:
            return result

        result.xiangting = 13  # シャン点数最大13
        unique_pais = self._get_unique_pais(pais)
        yaojiushu = len(
            [
                p
                for p in unique_pais
                if p.suit == "z" or (p.num in [1, 9] and p.suit in ["m", "p", "s"])
            ]
        )

        yaojiupai = Pai.get_yaojiupai()

        sorted_bingpai = sorted(pais, key=lambda x: (x.suit, x.num, x.is_red))

        # ヤオチュー牌が2枚以上あればシャン点数追加
        for p in yaojiupai:
            if Counter(sorted_bingpai)[p] >= 2:
                yaojiushu += 1
                break

        # シャン点数計算
        result.xiangting -= yaojiushu

        # アガリ牌を追加
        for y in yaojiupai:
            if result.xiangting != 0:
                break
            if set(yaojiupai).issubset(set(pais + [y])):
                result.hule_candidates.append(
                    PatternResult(pais + [y], [1 for _ in range(14)])
                )

        # ベストパターン設定
        result.best_candidates.append(PatternResult(pais, [1 for _ in range(13)]))

        # self.hule_candidates.extend(best_candidates)

        return result

    # チートイツシャン点数取得
    def _get_qiduizi_xiangting(self, pais: List[Pai] = []):
        result = XiangtingResult()
        if not pais:
            pais = self.bingpai
        if len(pais) < 13:
            return result

        result.xiangting = 6  # シャン点数最大6

        # 手牌の対子取得
        bingpai_str = [p.serialize(2) for p in pais]
        duizi_list = []
        single_list: List[str] = []
        kezi_list: List[str] = []
        gangzi_list: List[str] = []

        for s in bingpai_str:
            if Counter(bingpai_str)[s] == 2:
                duizi_list.append(s)
            elif Counter(bingpai_str)[s] == 3:
                kezi_list.append(s)
            elif Counter(bingpai_str)[s] == 4:
                gangzi_list.append(s)
            else:
                single_list.append(s)

        # シャン点数計算
        result.xiangting -= (
            (len(duizi_list) // 2) + (len(kezi_list) // 3) + (len(gangzi_list) // 4)
        )
        result.xiangting += (
            result.xiangting + 1 - len(single_list)
            if result.xiangting + 1 - len(single_list) > 0
            else 0
        )

        # アガリ牌設定
        for s in bingpai_str:
            if result.xiangting != 0:
                break
            if Counter(bingpai_str)[s] == 1:
                result.hule_candidates.append(
                    PatternResult(pais + [Pai.deserialize(s)], [2, 2, 2, 2, 2, 2, 2])
                )
                break

        # ベストパターン設定
        result.best_candidates.append(
            PatternResult(
                pais=pais,
                nums=[2 for _ in range(len(duizi_list) // 2)]
                + [1 for _ in range(len(single_list))],
            )
        )

        return result

    # 面子手牌シャン点数取得
    def _get_mianzi_xiangting(self, pais: List[Pai] = []):
        result = XiangtingResult(xiangting=8)
        temp_candidates: List[PatternResult] = []
        if not pais:
            pais = self.bingpai

        pattern_list = self._find_mianzi_pattern(pais)
        fulou_num = (13 - len(pais)) // 3
        result.xiangting = result.xiangting - fulou_num * 2
        min_block_num = min([len(pat.nums) for pat in pattern_list])
        # hule_candidates: List[PatternResult] = []
        for pat in pattern_list:
            if len(pat.nums) > min_block_num:
                continue
            if len(pat.pais) > 13 or len(pat.pais) % 3 != 1:
                raise ValueError(f"手牌の解析ができませんでした:{pat.pais}")
            tazi_num, mianzi_num, gangzi_num = [
                Counter(pat.nums)[i] for i in range(2, 5)
            ]  # ターツ数,面子数,槓子数
            jiangpai_idx = self._get_jiangpai_idx(pat)  # 雀頭有無

            xiangting = 8 - fulou_num * 2  # 初期シャン点数
            xiangting -= mianzi_num * 2  # 面子数分シャン点数を引く
            xiangting -= bool(jiangpai_idx)  # 雀頭があればシャン点数引く
            xiangting -= (
                tazi_num - bool(jiangpai_idx)
                if tazi_num
                <= 4 - fulou_num - mianzi_num  # 最大ブロック数=4-副露数-面子数
                else 4 - fulou_num - mianzi_num
            )  # ターツ数分シャン点数を引く
            # print("pat", [p.serialize() for p in pat.pais], pat.nums)
            # 雀頭なしかつ孤立牌が全て雀頭待ちにならない場合はシャン点数足す(最後の４枚が槓子の形)
            if (
                1 in pat.nums
                and 3 in pat.nums
                and not bool(jiangpai_idx)
                and all(
                    [pat.get_pais_by_num(i)[0] for _ in range(3)] in pat.get_pai_list()
                    for (i, n) in enumerate(pat.nums)
                    if n == 1
                )
            ):
                xiangting += 1
            # 雀頭ありかつ対子が刻子にならない場合はシャン点数足す(最後の４枚が槓子の形)
            if (
                2 in pat.nums
                and len(jiangpai_idx) >= 2
                and all(
                    pat.get_pais_by_num(i)
                    in [r for j, r in enumerate(pat.get_pai_list()) if i != j]
                    for (i, n) in enumerate(pat.nums)
                    if n == 2
                )
            ):
                xiangting += 1
            # if all(len(jiangpai_idx)>=2  and [p for j,p in enumerate(pat.pais) if sum(pat.nums[:i])<=j<sum(pat.nums[:i])+2]
            #     for (i,n) in enumerate(pat.nums) if n==2) :
            #     xiangting+=1
            # for (i,n) in enumerate(pat.nums):
            #     if not bool(jiangpai_idx) and n==1 and 3 in pat.nums and [pat.pais[sum(pat.nums[:i])] for _ in range(3)] in pat.pais:

            #     if bool(jiangpai_idx)  and n==2 and len(jiangpai_idx)>=2 and Counter(pat.pais)[pat.pais[sum(pat.nums[:i])]]!=4:
            #         xiangting+=1

            # シャン点数更新
            if xiangting < result.xiangting:
                result.xiangting = xiangting
                temp_candidates = []
                temp_candidates.append(pat)
            elif xiangting == result.xiangting:
                temp_candidates.append(pat)

            # テンパイであればアガリ牌を取得
            # if xiangting==0:
            #     self.hule_candidates+=self._compute_mianzi_hule_candidates(pat)

            # print(
            #     "pat,has_jiangpai,has_jiangpai,xiangting,hule_pais",
            #     "+".join([p.serialize(2) for p in pat.pais]),
            #     pat.nums,
            #     jiangpai_idx,
            #     xiangting,
            #     [p.serialize(2) for p in hule_pais],
            # )

        # アガリ候補追加
        for pat in temp_candidates:
            if result.xiangting != 0:
                break
            result.hule_candidates += self._compute_mianzi_hule_candidates(pat)
        result.hule_candidates.sort(key=lambda x: x.pais[-1].serialize())

        # ベストパターン設定
        result.best_candidates = temp_candidates

        return result

    def _get_jiangpai_idx(self, pattern: PatternResult):
        return [
            i
            for (i, n) in enumerate(pattern.nums)
            if n == 2
            and pattern.pais[sum(pattern.nums[:i])]
            == pattern.pais[sum(pattern.nums[:i]) + 1]
        ]  # 雀頭有無

    def _compute_mianzi_hule_candidates(self, pattern: PatternResult):
        hule_candidates: List[PatternResult] = []
        jiangpai_idx = self._get_jiangpai_idx(pattern)

        if len(jiangpai_idx) == 0:  # 単騎
            hule_candidates.append(
                PatternResult(pattern.pais + [pattern.pais[-1]], pattern.nums[:-1]+[pattern.nums[-1]+1])
            )

        elif len(jiangpai_idx) == 1:  # 対子＋ターツ
            p1, p2 = pattern.pais[-2], pattern.pais[-1]
            hule_candidates.extend(
                [
                    PatternResult(
                        pattern.pais + [Pai(suit=p1.suit, num=n)], pattern.nums[:-1]+[pattern.nums[-1]+1]
                    )
                    for n in range(1, 10)
                    if self._is_shunzi([p1, p2, Pai(suit=p1.suit, num=n)])
                ]
            )
        elif len(jiangpai_idx) == 2:  # 対子＋対子
            hule_candidates.extend(
                [
                    PatternResult(pattern.pais + [p], pattern.nums[:-1]+[pattern.nums[-1]+1])
                    for p in [pattern.pais[-4], pattern.pais[-2]]
                ]
            )
        return hule_candidates

    def _is_kezi(self, pais: List[Pai]):
        return (
            len(pais) == 3
            and pais[0].suit == pais[1].suit == pais[2].suit
            and pais[0].num == pais[1].num == pais[2].num
        )

    # def is_gangzi(self,pais: List[Pai]):
    #     return (
    #         len(pais) == 4
    #         and pais[0].suit == pais[1].suit == pais[2].suit == pais[3].suit
    #         and pais[0].num == pais[1].num == pais[2].num == pais[3].num
    #     )

    def _is_duizi(self, pais: List[Pai]):
        return (
            len(pais) == 2
            and pais[0].suit == pais[1].suit
            and pais[0].num == pais[1].num
        )

    def _is_shunzi(self, pais: List[Pai]):
        sorted_pais = sorted(pais, key=lambda x: (x.suit, x.num, x.is_red))
        return (
            len(sorted_pais) == 3
            and sorted_pais[0].suit == pais[1].suit == pais[2].suit
            and sorted_pais[0].suit in ["m", "p", "s"]
            and sorted_pais[0].num + 2 == sorted_pais[1].num + 1 == sorted_pais[2].num
        )

    def _is_tazi(self, pais: List[Pai]):
        return (
            len(pais) == 2
            and pais[0].suit == pais[1].suit
            and pais[0].suit in ["m", "p", "s"]
            and (
                abs(pais[0].num - pais[1].num) == 1
                or abs(pais[0].num - pais[1].num) == 2
            )
        )

    def _find_mianzi_pattern(
        self,
        pais: List[Pai],
        parent_combi: Optional[Tuple[int, List[Pai]]] = None,
        current_nest_num: int = 0,
    ) -> List[PatternResult]:
        pattern_list: List[PatternResult] = []
        pai_combination_list = self._find_pai_combinations(pais)
        pai_combination_list["gangzi"] = []

        # 各パターンタイプについて試行
        for i, (combination_type, pai_combinations) in enumerate(
            pai_combination_list.items()
        ):
            if (
                len(pais) > 4
                and combination_type in ["duizi", "tazi"]
                and len(pai_combination_list["kezi"] + pai_combination_list["shunzi"])
                > 0
            ):
                continue

            for j, combi_str in enumerate(pai_combinations):
                combi_pai = [Pai.deserialize(str) for str in combi_str.split("+")]
                filtered_pais = [Pai(suit=p.suit, num=p.num) for p in pais]
                # 使用した牌を除外
                for p in combi_pai:
                    # print("filtered_pais,combi_pai",[p.serialize(2) for p in filtered_pais],p)
                    filtered_pais.remove(p)

                # 再帰的に処理を継続
                recursive_patterns: List[PatternResult] = []
                if (
                    parent_combi is None
                    or (parent_combi[0] < i)
                    or (
                        parent_combi[0] == i
                        and parent_combi[1][0].serialize(2)
                        <= combi_pai[0].serialize(2)
                    )
                ):

                    recursive_patterns = self._find_mianzi_pattern(
                        filtered_pais,
                        (i, combi_pai),
                        current_nest_num + 1,
                    )
                    for pr in recursive_patterns:
                        pattern_list.append(
                            PatternResult(
                                combi_pai + pr.pais, [len(combi_pai)] + pr.nums
                            )
                        )
        pattern_list.append(PatternResult(pais, [1 for _ in range(len(pais))]))
        return pattern_list

    # def validate_combination(combination: dict) -> bool:
    #     """組み合わせが有効かどうかを検証"""
    #     gangzi_count = sum(
    #         1 for pattern_type, _ in combination["patterns"] if pattern_type == "ganzi"
    #     )
    #     return gangzi_count <= 1

    def _compute_xiangting(self):
        self.bingpai_candidates = []
        self.hule_candidates = []

        xiangting_patterns = {
            "kokushi": self._get_kokushi_xiangting(),
            "qiduizi": self._get_qiduizi_xiangting(),
            "mianzi": self._get_mianzi_xiangting(),
        }

        self.xiangting = min(
            pattern.xiangting for pattern in xiangting_patterns.values()
        )

        for pattern in xiangting_patterns.values():
            if pattern.xiangting == self.xiangting:
                self.bingpai_candidates.extend(pattern.best_candidates)
                self.hule_candidates.extend(pattern.hule_candidates)

        # print("xiangting,self.bingpai_candidates",self.xiangting,[ ("+".join([ x.serialize(2) for x in p.pais]),p.nums) for p in self.bingpai_candidates])

        return self.xiangting

    def _find_pai_combinations(self, pais: List[Pai]):
        """すべての可能なパターン（面子、刻子、対子、ターツ）を抽出"""
        patterns: Dict[Combination, List[str]] = {
            "shunzi": [],
            "kezi": [],
            "duizi": [],
            "tazi": [],
            "gangzi": [],
        }

        if len(pais) < 2:
            return patterns

        pais_str = [p.serialize(2) for p in pais]

        # 対子,刻子,槓子を探索
        for s in pais_str:
            duizi_str = "+".join([s, s])
            if Counter(pais_str)[s] > 1 and duizi_str not in patterns["duizi"]:
                patterns["duizi"].append(duizi_str)
            else:
                continue

            kezi_str = "+".join([s, s, s])
            if Counter(pais_str)[s] > 2 and duizi_str not in patterns["kezi"]:
                patterns["kezi"].append(kezi_str)
            else:
                continue

            gangzi_str = "+".join([s, s, s, s])
            if Counter(pais_str)[s] > 3 and duizi_str not in patterns["gangzi"]:
                patterns["gangzi"].append(gangzi_str)
            else:
                continue

        # 順子、ターツを探索
        for s in pais_str:
            if s[0] == "z":
                continue
            pair1, pair2 = f"{s[0]}{int(s[1])+1}", f"{s[0]}{int(s[1])+2}"
            lianmian, kanchan, shunzi = (
                "+".join([s, pair1]),
                "+".join([s, pair2]),
                "+".join([s, pair1, pair2]),
            )
            if Counter(pais_str)[pair1] > 0 and lianmian not in patterns["tazi"]:
                patterns["tazi"].append(lianmian)
            if Counter(pais_str)[pair2] > 0 and kanchan not in patterns["tazi"]:
                patterns["tazi"].append(kanchan)
            if (
                Counter(pais_str)[pair1] > 0
                and Counter(pais_str)[pair2] > 0
                and shunzi not in patterns["shunzi"]
            ):
                patterns["shunzi"].append(shunzi)

        # print("pais pattern","+".join([p.serialize(2) for p in pais]),[(k,patterns[k]) for (k) in patterns.keys()])

        return patterns

    def _comupute_lizhi_candidates(self):
        self.lizhi_pai = []

        lizhi_pai: List[Pai] = []

        # 下記条件であるときは処理しない
        if (
            self.xiangting > 1  # シャン点数１より大きい
            or len(self.bingpai) < 13
            or (
                self.fulou and [f for f in self.fulou if f.type != "angang"]
            )  # 副露が暗槓以外ある
            or not self.zimopai  # ツモ牌が存在しない
            or self.lizhi_flag #立直中
        ):
            return lizhi_pai

        # リーチ牌探索
        replaced_pais_str: List[str] = []

        # 手牌の１枚をツモ牌に置き換えたパターン取得
        for i, p in enumerate(self.bingpai):
            pais_str = "+".join(
                [q.serialize(2) for j, q in enumerate(self.bingpai) if i != j]
                + [self.zimopai.serialize(2)]
                + [p.serialize(2)]
            )
            if pais_str not in replaced_pais_str:
                replaced_pais_str.append(pais_str)

        # 手牌パターン追加
        if self.zimopai.serialize(2) not in [
            s.serialize(2) for s in self.bingpai
        ]:
            replaced_pais_str.append(
                "+".join(
                    [p.serialize(2) for p in self.bingpai]
                    + [self.zimopai.serialize(2)]
                )
            )

        # リーチ牌探索
        for pais_str in replaced_pais_str:
            replaced_pais = [Pai.deserialize(s) for s in pais_str.split("+")]
            xiangting_result = {
                "kokushi": self._get_kokushi_xiangting(replaced_pais[:-1]),
                "qiduizi": self._get_qiduizi_xiangting(replaced_pais[:-1]),
                "mianzi": self._get_mianzi_xiangting(replaced_pais[:-1]),
            }
            xiangting = min(pattern.xiangting for pattern in xiangting_result.values())

            if xiangting == 0:
                lizhi_pai.append(replaced_pais[-1])

        self.lizhi_pai = lizhi_pai
        return lizhi_pai
    
    def get_fuloupais(self):
        return [p for f in self.fulou for p in f.get_pais()]
    
    def get_serialized_fulou_candidates(self):
        if not self.fulou_candidates:
            return None
        return "|".join([f.serialize() for f in self.fulou_candidates])
    
    def get_serialized_lizhi_pai(self):
        if not self.lizhi_pai:
            return None
        return "+".join([p.serialize() for p in self.lizhi_pai])
    
    def get_serialized_hule_pai(self):
        if not self.hule_candidates:
            return None
        return "+".join([pat.pais[-1].serialize() for pat in self.hule_candidates])
