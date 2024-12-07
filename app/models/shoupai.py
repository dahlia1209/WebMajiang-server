from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional, NamedTuple
from .pai import Pai
from collections import defaultdict
from .type import Feng, PlayerAction, Position, Combination
from collections import Counter
from dataclasses import dataclass
from copy import deepcopy
import warnings

FulouType = Literal["chi", "peng", "minggang", "angang", "jiagang"]


@dataclass
class PatternResult:
    pais: List[Pai]
    nums: List[int]


class Fulou(BaseModel):
    type: FulouType
    nakipai: Optional[Pai] = Field(default=None)
    fuloupais: Optional[List[Pai]] = Field(default=[])
    position: Optional[Position] = Field(default=None)

    def serialize(self, without_red: bool = False) -> str:
        point = 2 if without_red else 3
        ns = self.nakipai.serialize()[:point] if self.nakipai else "null"
        fs = (
            "+".join(p.serialize()[:point] for p in self.fuloupais)
            if self.fuloupais
            else "null"
        )
        ps = self.position if self.position else "null"
        s = ",".join([str(self.type), ns, fs, ps])
        return s
    
    def get_without_red(self):
        return Fulou(
            type=self.type,
            nakipai=(
                Pai(suit=self.nakipai.suit, num=self.nakipai.num)
                if self.nakipai
                else None
            ),
            fuloupais=[Pai(suit=p.suit, num=p.num) for p in self.fuloupais],
            position=self.position
        )

    @staticmethod
    def deserialize(s: str) -> "Fulou":
        ss = s.split(",")
        if len(ss) != 4:
            raise ValueError(f"指定した文字列に誤りがあります:{s}")

        t = ss[0]  # FulouType
        n = None if ss[1] == "null" else Pai.deserialize(ss[1])
        f = [] if ss[2] == "null" else [Pai.deserialize(fs) for fs in ss[2].split("+")]
        p = None if ss[3] == "null" else ss[3]

        return Fulou(type=t, nakipai=n, fuloupais=f, position=p)


class Shoupai(BaseModel):
    bingpai: List[Pai] = Field(default=[])
    fulou: List[Fulou] = Field(default=[])
    zimopai: Optional[Pai] = Field(default=None)
    hule_candidates: List[PatternResult] = Field(default=[])
    fulou_candidates: List[Fulou] = Field(default=[])
    lizhi_candidates: List[Fulou] = Field(default=[])
    xiangting: int = Field(default=99)
    bingpai_candidates: List[PatternResult] = Field(default=[])
    is_lizhi: bool = Field(default=False)
    is_hule:bool=Field(default=False)

    def do_zimo(self, pai: Pai):
        if self.zimopai is not None:
            raise ValueError(f"ツモ牌がすでに存在します.zimopai:{self.zimopai}")
        self.zimopai = pai

        # アガリ形の確認
        # self._check_hule()

        # リーチ候補探索
        if not self.is_lizhi:
            self._comupute_lizhi_candidates()

        # 副露候補候補
        self._compute_fulou_candidates(fulou_type=["angang", "jiagang"])

    def do_dapai(self, dapai: Pai, dapai_idx: int):
        dapai: Pai
        if 0 <= dapai_idx < len(self.bingpai):
            if self.bingpai[dapai_idx] != dapai:
                raise ValueError(
                    f"牌番号と打牌が一致していません.牌番号:{dapai_idx},牌番号の手牌:{self.bingpai[dapai_idx]},打牌:{dapai}"
                )
            if self.is_lizhi:
                raise ValueError(f"リーチ中に手牌から打牌しています")
            dapai = self.bingpai.pop(dapai_idx)
        elif dapai_idx == 99:
            if self.zimopai.serialize() != dapai.serialize():
                raise ValueError(
                    f"ツモ牌と打牌が一致していません.牌番号:{dapai_idx},ツモ牌:{self.zimopai},打牌:{dapai}"
                )
            dapai = self.zimopai
            self.zimopai = None
        else:
            raise ValueError(
                f"指定したインデックスは正しくありません.idx={dapai_idx},手牌数={len(self.bingpai)}"
            )

        # ツモ牌を手牌に加えてソート
        sorted_pais = sorted(
            self.bingpai + ([self.zimopai] if self.zimopai else []),
            key=lambda x: (x.suit, x.num, x.is_red),
        )
        self.zimopai=None
        self.bingpai = sorted_pais

        # 副露候補候補
        self._compute_fulou_candidates(fulou_type=["chi", "peng", "minggang"])

        # アガリ系探索
        self._compute_xiangting()
        
        return dapai

    def do_fulou(self, fulou: Fulou):
        """副露（チー、ポン、明槓、暗槓、加槓）を実行する汎用関数"""
        fulou_without_red = fulou.get_without_red()
        if fulou_without_red.model_copy(update={"position":None}) not in self.fulou_candidates:
            raise ValueError(
                f"指定された副露はできません。指定された副露{fulou.serialize()}.副露候補:{[f.serialize() for f in self.fulou_candidates]}"
            )
            
        if fulou_without_red.type in ["chi","peng","minggang"] and not fulou.position:
            raise ValueError(
                f"副露の鳴き先が指定されていません.副露:{fulou.serialize()}."
            )

        if fulou.type == "jiagang":
            fulou_copy = fulou.model_copy(update={"type": "peng"})
            bingpai: List[Pai] = []
            jiapai: Pai
            fulou_idx = self.fulou.index(fulou_copy)
            # 手牌からカカン牌を抜く
            for p in self.bingpai + ([self.zimopai] if self.zimopai else []):
                if p.serialize()[:2] == fulou_copy.nakipai.serialize()[:2]:
                    jiapai = p
                else:
                    bingpai.append(p)
            self.bingpai = sorted(bingpai, key=lambda x: (x.suit, x.num, x.is_red))
            self.zimopai=None

            # 副露牌にカカン牌を追加
            fulou_copy = self.fulou[fulou_idx].model_copy(update={"type": "jiagang"})
            fulou_copy.fuloupais.append(jiapai)
            self.fulou[fulou_idx] = fulou_copy

        elif fulou.type == "angang":
            fulou_copy = fulou.model_copy()
            angang_pai: List[Pai] = []
            bingpai: List[Pai] = []
            for p in self.bingpai + ([self.zimopai] if self.zimopai else []):
                if p.serialize()[:2] == fulou.fuloupais[0].serialize()[:2]:
                    angang_pai.append(p)
                else:
                    bingpai.append(p)
            fulou_copy.fuloupais = angang_pai
            self.bingpai = sorted(bingpai, key=lambda x: (x.suit, x.num, x.is_red))
            self.zimopai=None
            
            self.fulou.append(fulou_copy)

        elif fulou.type in ["chi", "minggang", "peng"]:
            self.fulou.append(fulou)
            for p in fulou.fuloupais:
                self.bingpai.remove(p)

        else:
            raise ValueError(f"副露できません:{fulou}")
        
        if fulou.type in ["chi","peng"]:
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
            if self.is_lizhi:
                raise ValueError(f"リーチ中に手牌から打牌しています")
            dapai = self.bingpai.pop(dapai_idx)
        elif dapai_idx == 99:
            if self.zimopai.serialize() != dapai.serialize():
                raise ValueError(
                    f"ツモ牌と打牌が一致していません.牌番号:{dapai_idx},ツモ牌:{self.zimopai},打牌:{dapai}"
                )
            dapai = self.zimopai
            self.zimopai = None
        else:
            raise ValueError(
                f"指定したインデックスは正しくありません.idx={dapai_idx},手牌数={len(self.bingpai)}"
            )
        return True

    def do_lizhi(self, dapai: Pai, dapai_idx: int):
        dapai: Pai
        if 0 <= dapai_idx < len(self.bingpai):
            if self.bingpai[dapai_idx] != dapai:
                raise ValueError(
                    f"牌番号と打牌が一致していません.牌番号:{dapai_idx},牌番号の手牌:{self.bingpai[dapai_idx]},打牌:{dapai}"
                )
            if self.is_lizhi:
                raise ValueError(f"リーチ中に手牌から打牌しています")
            dapai = self.bingpai.pop(dapai_idx)
        elif dapai_idx == 99:
            if self.zimopai.serialize() != dapai.serialize():
                raise ValueError(
                    f"ツモ牌と打牌が一致していません.牌番号:{dapai_idx},ツモ牌:{self.zimopai},打牌:{dapai}"
                )
            dapai = self.zimopai
            self.zimopai = None
        else:
            raise ValueError(
                f"指定したインデックスは正しくありません.idx={dapai_idx},手牌数={len(self.bingpai)}"
            )

        # ツモ牌を手牌に加えてソート
        sorted_pais = sorted(
            self.bingpai + ([self.zimopai] if self.zimopai else []),
            key=lambda x: (x.suit, x.num, x.is_red),
        )
        self.zimopai=None
        self.bingpai = sorted_pais

        # アガリ系探索
        self._compute_xiangting()
        
        return dapai

    def _compute_fulou_candidates(
        self,
        fulou_type: List[FulouType] = ["chi", "peng", "minggang", "angang", "jiagang"],
        combination_list: Dict[Combination, List[str]] = {},
    ):
        fulou_candidates: List[Fulou] = []
        if len(self.bingpai) == 1:
            return fulou_candidates
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
                        Fulou(type="chi", nakipai=x, fuloupais=[t1, t2])
                    )

        # ポン候補
        for pai_str in combination_list["duizi"]:
            if "peng" not in fulou_type:
                break
            p1, p2 = [Pai.deserialize(s) for s in pai_str.split("+")]
            fulou_candidates.append(Fulou(type="peng", nakipai=p1, fuloupais=[p1, p2]))

        # 明槓候補
        for pai_str in combination_list["kezi"]:
            if "minggang" not in fulou_type:
                break
            m1, m2, m3 = [Pai.deserialize(s) for s in pai_str.split("+")]
            fulou_candidates.append(
                Fulou(type="minggang", nakipai=m1, fuloupais=[m1, m2, m3])
            )


        # 暗槓候補
        for pai_str in combination_list["kezi"]:
            if "angang" not in fulou_type:
                break
            m1, m2, m3 = [Pai.deserialize(s) for s in pai_str.split("+")]
            if self.zimopai and self.zimopai.serialize()[:2] == m1.serialize()[:2]:
                fulou_candidates.append(
                    Fulou(type="angang", fuloupais=[m1, m2, m3, m1])
                )
        for pai_str in combination_list["gangzi"]:
            if "angang" not in fulou_type:
                break
            a1, a2, a3, a4 = [Pai.deserialize(s) for s in pai_str.split("+")]
            fulou_candidates.append(Fulou(type="angang", fuloupais=[a1, a2, a3, a4]))

        # 加槓候補
        for f in self.fulou:
            if "jiagang" not in fulou_type:
                break
            if f.type == "peng" and f.nakipai.serialize()[:2] in [
                p.serialize()[:2]
                for p in self.bingpai + ([self.zimopai] if self.zimopai else [])
            ]:
                fulou_candidates.append(
                    Fulou(type="jiagang", nakipai=f.nakipai, fuloupais=f.fuloupais)
                )

        self.fulou_candidates = fulou_candidates

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
        xiangting: int = 99
        best_candidates: List[PatternResult] = []
        hule_candidates: List[PatternResult] = []
        if not pais:
            pais = self.bingpai
        if len(pais) < 13:
            return (xiangting, best_candidates,hule_candidates)

        xiangting = 13  # シャン点数最大13
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
        xiangting -= yaojiushu

        # アガリ牌を追加
        for y in yaojiupai:
            if xiangting != 0:
                break
            if set(yaojiupai).issubset(set(pais + [y])):
                hule_candidates.append(
                    PatternResult(pais + [y], [1 for _ in range(14)])
                )

        # ベストパターン設定
        best_candidates.append(PatternResult(pais, [1 for _ in range(13)]))

        # self.hule_candidates.extend(best_candidates)

        return (xiangting, best_candidates,hule_candidates)

    # チートイツシャン点数取得
    def _get_qiduizi_xiangting(self, pais: List[Pai] = []):
        xiangting: int = 99
        best_candidates: List[PatternResult] = []
        hule_candidates: List[PatternResult] = []
        if not pais:
            pais = self.bingpai
        if len(pais) < 13:
            return (xiangting, best_candidates,hule_candidates)

        xiangting = 6  # シャン点数最大6

        # 手牌の対子取得
        bingpai_str = [p.serialize()[:2] for p in pais]
        duizi_list = []
        single_list: List[str] = []
        for s in bingpai_str:
            if Counter(bingpai_str)[s] == 2:
                duizi_list.append(s)
            else:
                single_list.append(s)

        # シャン点数計算
        xiangting -= len(duizi_list) / 2

        # アガリ牌設定
        for s in bingpai_str:
            if xiangting != 0:
                break
            if Counter(bingpai_str)[s] == 1:
                hule_candidates.append(
                    PatternResult(pais + [Pai.deserialize(s)], [2, 2, 2, 2, 2, 2, 1, 1])
                )
                break

        # ベストパターン設定
        best_candidates.append(
            PatternResult(
                pais=pais,
                nums=[2 for _ in range(len(duizi_list) // 2)]
                + [1 for _ in range(len(single_list))],
            )
        )

        return xiangting, best_candidates,hule_candidates

    # 面子手牌シャン点数取得
    def _get_mianzi_xiangting(self, pais: List[Pai] = []):
        best_xiangting: int = 8
        hule_candidates: List[PatternResult] = []
        best_candidates: List[PatternResult] = []
        temp_candidates: List[PatternResult] = []
        if not pais:
            pais = self.bingpai

        combination_list = self._find_combinations(pais)
        fulou_num = (13 - len(pais)) / 3
        best_xiangting = best_xiangting - fulou_num * 2
        min_block_num = min(
            [len(pat.nums) for pat in combination_list if 4 not in pat.nums]
        )
        # hule_candidates: List[PatternResult] = []
        for pat in combination_list:
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
            xiangting -= gangzi_num  # 槓子数分シャン点数を引く

            # シャン点数更新
            if xiangting < best_xiangting:
                best_xiangting = xiangting
                temp_candidates = []
                temp_candidates.append(pat)
            elif xiangting == best_xiangting:
                temp_candidates.append(pat)

            # テンパイであればアガリ牌を取得
            # if xiangting==0:
            #     self.hule_candidates+=self._compute_mianzi_hule_candidates(pat)

            # print(
            #     "pat,has_jiangpai,has_jiangpai,xiangting,hule_pais",
            #     "+".join([p.serialize()[:2] for p in pat.pais]),
            #     pat.nums,
            #     jiangpai_idx,
            #     xiangting,
            #     [p.serialize()[:2] for p in hule_pais],
            # )

        # アガリ候補追加
        for pat in temp_candidates:
            if best_xiangting != 0:
                break
            hule_candidates += self._compute_mianzi_hule_candidates(pat)
        hule_candidates.sort(key=lambda x: x.pais[-1].serialize())

        # ベストパターン設定
        best_candidates = temp_candidates

        return best_xiangting, best_candidates,hule_candidates

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
                PatternResult(pattern.pais + [pattern.pais[-1]], pattern.nums + [1])
            )

        elif len(jiangpai_idx) == 1:  # 対子＋ターツ
            p1, p2 = pattern.pais[-2], pattern.pais[-1]
            hule_candidates.extend(
                [
                    PatternResult(
                        pattern.pais + [Pai(suit=p1.suit, num=n)], pattern.nums + [1]
                    )
                    for n in range(1, 10)
                    if self._is_shunzi([p1, p2, Pai(suit=p1.suit, num=n)])
                ]
            )
        elif len(jiangpai_idx) == 2:  # 対子＋対子
            hule_candidates.extend(
                [
                    PatternResult(pattern.pais + [p], pattern.nums + [1])
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

    def _find_combinations(
        self,
        pais: List[Pai],
        parent_combi: Optional[Tuple[int, List[Pai]]] = None,
        current_nest_num: int = 0,
    ) -> List[PatternResult]:
        pattern_list: List[PatternResult] = []
        pai_combination_list = self._find_pai_combinations(pais)
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
                filtered_pais =  [Pai(suit=p.suit,num=p.num) for p in pais]
                # 使用した牌を除外
                for p in combi_pai:
                    # print("filtered_pais,combi_pai",[p.serialize()[:2] for p in filtered_pais],p)
                    filtered_pais.remove(p)

                # 再帰的に処理を継続
                recursive_patterns: List[PatternResult] = []
                if (
                    parent_combi is None
                    or (parent_combi[0] < i)
                    or (
                        parent_combi[0] == i
                        and parent_combi[1][0].serialize()[:2]
                        <= combi_pai[0].serialize()[:2]
                    )
                ):

                    recursive_patterns = self._find_combinations(
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
            'kokushi': self._get_kokushi_xiangting(),
            'qiduizi': self._get_qiduizi_xiangting(),
            'mianzi': self._get_mianzi_xiangting()
        }
        
        self.xiangting = min(pattern[0] for pattern in xiangting_patterns.values())
        
        for pattern in xiangting_patterns.values():
            if pattern[0] == self.xiangting:
                self.bingpai_candidates.extend(pattern[1])
                self.hule_candidates.extend(pattern[2])
                
        # self.hule_candidates.sort(key=lambda x: x.pais[-1].serialize())

        # kokushi_xiangting, kokushi_pattern,kokushi_hule = self._get_kokushi_xiangting()
        # qiduizi_xiangting, qiduizi_pattern,qiduizi_hule = self._get_qiduizi_xiangting()
        # mianzi_xiangting, mianzi_pattern,mianzi_hule = self._get_mianzi_xiangting()
        # self.hule_candidates.sort(key=lambda x: x.pais[-1].serialize())

        # self.xiangting = min(kokushi_xiangting, qiduizi_xiangting, mianzi_xiangting)
        # for x in [
        #     (kokushi_xiangting, kokushi_pattern,kokushi_hule),
        #     (qiduizi_xiangting, qiduizi_pattern,qiduizi_hule),
        #     (mianzi_xiangting, mianzi_pattern,mianzi_hule),
        # ]:
        #     if x[0] == self.xiangting:
        #         self.bingpai_candidates.extend(x[1])
        # self._comupute_lizhi_candidates()

        # self.bingpai_candidates.sort(key=lambda x: x.pais[-1].serialize())
        # print("xiangting,self.bingpai_candidates",self.xiangting,[ ("+".join([ x.serialize()[:2] for x in p.pais]),p.nums) for p in self.bingpai_candidates])

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

        pais_str = [p.serialize()[:2] for p in pais]

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

        # print("pais pattern","+".join([p.serialize()[:2] for p in pais]),[(k,patterns[k]) for (k) in patterns.keys()])

        return patterns

    def _comupute_lizhi_candidates(self):
        self.lizhi_candidates = []

        lizhi_candidates: List[PatternResult] = []

        # 下記条件であるときは処理しない
        if (
            self.xiangting > 1  # シャン点数１より大きい
            or self.bingpai !=13
            or (
                self.fulou and [f for f in self.fulou if f.type != "angang"]
            )  # 副露が暗槓以外ある
            or not self.zimopai  # ツモ牌が存在しない
        ):
            return lizhi_candidates

        # リーチ牌探索
        for pat in self.bingpai_candidates:
            replaced_pais_str: List[str] = []

            # 手牌パターン追加
            # replaced_pais_str.append("+".join([p.serialize() for p in pat.pais]+[self.zimopai.serialize()]))

            # 手牌の１枚をツモ牌に置き換えたパターン取得
            for i, p in enumerate(pat.pais):
                pais_str = "+".join(
                    [q.serialize() for j, q in enumerate(pat.pais) if i != j]
                    + [self.zimopai.serialize()]
                    + [p.serialize()]
                )
                if pais_str not in replaced_pais_str:
                    replaced_pais_str.append(pais_str)

            for pais_str in replaced_pais_str:
                replaced_pais = [Pai.deserialize(s) for s in pais_str.split("+")]
                x: int
                bs: list[PatternResult]
                if Counter(pat.nums)[2] >= 5:
                    x, bs = self._get_qiduizi_xiangting(replaced_pais[:-1])
                elif Counter(pat.nums)[1] == 13:
                    x, bs = self._get_kokushi_xiangting(replaced_pais[:-1])
                else:
                    x, bs = self._get_mianzi_xiangting(replaced_pais[:-1])

                if x == 0:
                    for b in bs:
                        lizhi_candidates.append(
                            PatternResult(b.pais + [replaced_pais[-1]], b.nums + [1])
                        )
                    self.hule_candidates = []

        self.lizhi_candidates = lizhi_candidates
        return lizhi_candidates
