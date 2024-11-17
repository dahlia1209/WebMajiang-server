from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Dict, Tuple, Literal, Optional
from .pai import Pai
from collections import defaultdict
from .type import Feng, PlayerAction, Position

FulouType = Literal["chi", "peng", "minggang", "angang", "jiagang"]


class Fulou(BaseModel):
    type: FulouType
    nakipai: Optional[Pai]=Field(default=None)
    fuloupais: Optional[List[Pai]]=Field(default=[])
    position: Optional[Position]=Field(default=None)
    
    def serialize(self) -> str:
        ns = self.nakipai.serialize() if self.nakipai else "null"
        fs = "+".join(p.serialize() for p in self.fuloupais) if self.fuloupais else "null"
        ps = self.position if self.position else "null"
        s = ",".join([str(self.type), ns, fs, ps])
        return s

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
    waiting_hule_pai: List[Pai] = Field(default=[])
    waiting_fulou_pai: List[Fulou] = Field(default=[])

    def add_pai(self, pai: Pai):
        """牌を手牌にセットする"""
        self.zimopai = pai
        self.zimo_into_bingpai()

    def set_zimopai(self, pai: Pai):
        """牌をツモ牌にセットする"""
        if self.zimopai is not None:
            raise ValueError("zimo is not None")
        self.zimopai = pai

    def get_zimo(self):
        """ツモ牌を取得する"""
        if self.zimopai is None:
            raise ValueError("zimo is None")
        return self.zimopai

    @staticmethod
    def sort_pai(pais: List[Pai]):
        sorted_pais = sorted(
            pais, key=lambda x: (x.suit, x.num, x.is_red)
        )
        return sorted_pais

    def remove_pai_from_zimopai(self):
        """ツモ牌を削除する"""
        if self.zimopai is not None:
            self.zimopai = None
        else:
            raise ValueError(f"zimopai is None")

    def remove_pai_from_bingpai(
        self, pai: Optional[Pai] = None, index: Optional[int] = None
    ):
        """手牌から1牌を削除する"""
        if pai is not None:
            self.bingpai.remove(pai)
        elif index is not None:
            self.bingpai.remove(self.bingpai[index])
        else:
            raise ValueError(f"pai or index is not given")

    def remove_pai(self, pai: Pai):
        if self.zimopai == pai:
            self.zimopai = None
            return
        self.bingpai.remove(pai)

    def zimo_into_bingpai(self):
        self.bingpai.append(self.zimopai)
        self.remove_pai_from_zimopai()

    def get_fulou_pai(self, pai: Pai):
        fulou_pai: List[Fulou] = []
        for f in self.waiting_fulou_pai:
            if f.nakipai.num == pai.num and f.nakipai.suit == pai.suit:
                fulou_pai.append(f)
        return fulou_pai

    def set_fulou_pai_from_shoupai(self):
        # ターツから副露候補を取得
        def get_fulou_from_dazi(pais: List[Pai]):
            fulou: List[Fulou] = []
            mianzi_pai = Shoupai.get_mianzi_pai(pais)
            for pai in mianzi_pai:
                fulou.append(
                    Fulou(
                        type="chi",
                        nakipai=Pai(num=pai.num, suit=pai.suit),
                        fuloupais=[
                            Pai(num=pais[0].num, suit=pais[0].suit),
                            Pai(
                                num=pais[1].num,
                                suit=pais[1].suit,
                            ),
                        ],
                    )
                )
            return fulou

        if len(self.bingpai) == 1:
            return []
        sort_pai = Shoupai.sort_pai(self.bingpai)
        unique_pais = Shoupai.remove_duplicates(sort_pai)
        waiting_fulo_pai: List[Fulou] = []

        # 搭子のチェック
        for i in range(len(unique_pais) - 1):
            if Shoupai.is_dazi(unique_pais[i : i + 2]):
                waiting_fulo_pai.extend(get_fulou_from_dazi(unique_pais[i : i + 2]))

            if i != (len(unique_pais) - 2) and Shoupai.is_dazi(
                [unique_pais[i], unique_pais[i + 2]]
            ):
                waiting_fulo_pai.extend(
                    get_fulou_from_dazi([unique_pais[i], unique_pais[i + 2]])
                )

        # 対子のチェック
        peng_pai: List[Pai] = []
        for i in range(len(sort_pai) - 1):
            if Shoupai.is_duizi(sort_pai[i : i + 2]):
                peng_pai.append(Pai(num=sort_pai[i].num, suit=sort_pai[i].suit))
        peng_pai = Shoupai.remove_duplicates(peng_pai)
        for p in peng_pai:
            waiting_fulo_pai.append(
                Fulou(
                    type="peng",
                    nakipai=p,
                    fuloupais=[p, p],
                )
            )

        # 刻子のチェック
        kezi_pai: List[Pai] = []
        for i in range(len(sort_pai) - 2):
            if Shoupai.is_kezi(sort_pai[i : i + 3]):
                kezi_pai.append(Pai(num=sort_pai[i].num, suit=sort_pai[i].suit))
        kezi_pai = Shoupai.remove_duplicates(kezi_pai)
        for p in kezi_pai:
            waiting_fulo_pai.append(
                Fulou(
                    type="minggang",
                    nakipai=p,
                    fuloupais=[p, p, p],
                )
            )

        self.waiting_fulou_pai = waiting_fulo_pai

    def get_main_fulou_pai(self):
        sort_pai = Shoupai.sort_pai([self.zimopai] + self.bingpai)
        fulou: List[Fulou] = []
        # 暗槓のチェック
        for i in range(len(sort_pai) - 3):
            if Shoupai.is_gangzi(sort_pai[i : i + 4]):
                fulou.append(
                    Fulou(
                        type="angang",
                        nakipai=None,
                        fuloupais=sort_pai[i : i + 4],
                    )
                )

        # 加槓のチェック
        peng_fulou = [f for f in self.fulou if f.type == "peng"]
        for f in peng_fulou:
            for p in sort_pai:
                if p.num == f.nakipai.num and p.suit == f.nakipai.suit:
                    fulou.append(
                        Fulou(
                            type="jiagang",
                            nakipai=f.nakipai,
                            fuloupais=f.fuloupais + [p],
                        )
                    )

        return fulou

    def do_fulou(self, fulou: Fulou):
        """副露（チー、ポン、明槓、暗槓、加槓）を実行する汎用関数"""
        if fulou.type == "jiagang":
            for i, f in enumerate(self.fulou):
                if f.type == "peng" and fulou.fuloupais[-1] in (
                    self.bingpai + [self.zimopai]
                ):
                    self.fulou[i].type = "jiagang"
                    self.fulou[i].fuloupais = fulou.fuloupais
                    break
            self.remove_pai(fulou.fuloupais[-1])
        elif fulou.type == "angang":
            for p in fulou.fuloupais:
                self.remove_pai(p)
            self.fulou.append(fulou)
            if self.zimopai is not None:
                self.bingpai.append(self.zimopai)
                self.remove_pai_from_zimopai()

        elif fulou in self.waiting_fulou_pai:
            self.fulou.append(fulou)
        else:
            raise ValueError(f"副露できません:{fulou}")

    def calculate_xiangting(self) -> Tuple[bool, List[Pai]]:
        """
        手牌がテンパイかどうかをチェックし、テンパイの場合はアガリ牌のリストを返す
        """
        is_tenpai = False
        agari_pais = []

        # メンゼンの場合のみ七対子と国士無双をチェック
        if not self.fulou:
            is_tenpai_qidui, agari_pais_qidui = self._check_qidui()
            is_tenpai_kokushi, agari_pais_kokushi = self._check_kokushi()
            if is_tenpai_qidui:
                is_tenpai = True
                agari_pais.extend(agari_pais_qidui)
            if is_tenpai_kokushi:
                is_tenpai = True
                agari_pais.extend(agari_pais_kokushi)

        # 4メンツ1雀頭のチェック
        is_tenpai_regular, agari_pais_regular = self._check_regular()
        if is_tenpai_regular:
            is_tenpai = True
            agari_pais.extend(agari_pais_regular)

        return is_tenpai, list(set(agari_pais))

    def _check_qidui(self) -> Tuple[bool, List[Pai]]:
        """
        七対子のテンパイ形をチェック
        """
        if self.fulou:  # 副露がある場合は七対子にならない
            return False, []

        pai_count = defaultdict(int)
        for pai in self.bingpai:
            pai_count[(pai.suit, pai.num)] += 1

        pairs = sum(1 for count in pai_count.values() if count >= 2)
        single = sum(1 for count in pai_count.values() if count == 1)

        if pairs == 6 and single == 1:
            agari_pais = [
                Pai(suit=suit, num=num)
                for (suit, num), count in pai_count.items()
                if count == 1
            ]
            return True, agari_pais
        return False, []

    def _check_kokushi(self) -> Tuple[bool, List[Pai]]:
        """
        国士無双のテンパイ形をチェック
        """
        if self.fulou:
            return False, []

        yaochuupai = [
            ("m", 1),
            ("m", 9),
            ("p", 1),
            ("p", 9),
            ("s", 1),
            ("s", 9),
            ("z", 1),
            ("z", 2),
            ("z", 3),
            ("z", 4),
            ("z", 5),
            ("z", 6),
            ("z", 7),
        ]
        pai_count = defaultdict(int)
        for pai in self.bingpai:
            if (pai.suit, pai.num) in yaochuupai:
                pai_count[(pai.suit, pai.num)] += 1

        if len(pai_count) == 13:  # 13面待ち
            return True, [Pai(suit=suit, num=num) for (suit, num) in yaochuupai]
        elif len(pai_count) == 12 and sum(pai_count.values()) == 13:  # 単騎待ち
            missing_pai = next(
                (
                    Pai(suit=suit, num=num)
                    for (suit, num) in yaochuupai
                    if (suit, num) not in pai_count
                ),
                None,
            )
            return True, [missing_pai] if missing_pai else []
        return False, []

    @staticmethod
    def is_shunzi(pais: List[Pai]) -> bool:
        # 順子
        sort_pai = Shoupai.sort_pai(pais)
        return (
            len(pais) == 3
            and sort_pai[0].suit == sort_pai[1].suit == sort_pai[2].suit != "z"
            and sort_pai[2].num == sort_pai[1].num + 1 == sort_pai[0].num + 2
        )

    @staticmethod
    def is_kezi(pais: List[Pai]) -> bool:
        # 刻子
        return (
            len(pais) == 3
            and pais[0].suit == pais[1].suit == pais[2].suit
            and pais[0].num == pais[1].num == pais[2].num
        )

    @staticmethod
    def is_gangzi(pais: List[Pai]) -> bool:
        # 槓子
        return (
            len(pais) == 4
            and pais[0].suit == pais[1].suit == pais[2].suit == pais[3].suit
            and pais[0].num == pais[1].num == pais[2].num == pais[3].num
        )

    @staticmethod
    def is_duizi(pais: List[Pai]) -> bool:
        # 対子
        return (
            len(pais) == 2
            and pais[0].suit == pais[1].suit
            and pais[0].num == pais[1].num
        )

    @staticmethod
    def is_dazi(pais: List[Pai]) -> bool:
        # 搭子
        sort_pai = Shoupai.sort_pai(pais)
        return (
            len(sort_pai) == 2
            and sort_pai[0].suit == sort_pai[1].suit != "z"
            and (
                sort_pai[1].num == sort_pai[0].num + 1
                or sort_pai[1].num == sort_pai[0].num + 2
            )
        )

    @staticmethod
    def get_mianzi_pai(pais: List[Pai]) -> List[Pai]:
        if Shoupai.is_duizi(pais):
            return [Pai(num=pais[0].num, suit=pais[0].suit)]
        elif Shoupai.is_dazi(pais):
            sort_pai = Shoupai.sort_pai(pais)
            if sort_pai[1].num - sort_pai[0].num == 2:
                # カンチャン
                return [Pai(num=pais[0].num + 1, suit=pais[0].suit)]
            elif sort_pai[0].num == 1 or sort_pai[1].num == 9:
                # ペンチャン
                return [
                    (
                        Pai(num=3, suit=pais[0].suit)
                        if sort_pai[0].num == 1
                        else Pai(num=7, suit=pais[0].suit)
                    )
                ]
            elif sort_pai[0].num + 1 == sort_pai[1].num:
                # 両面
                return [
                    Pai(num=pais[0].num - 1, suit=pais[0].suit),
                    Pai(num=pais[1].num + 1, suit=pais[1].suit),
                ]

        else:
            return []

    @staticmethod
    def remove_duplicates(pais: List[Pai]) -> List[Pai]:
        seen = set()
        unique_pais = []
        for pai in pais:
            key = (pai.suit, pai.num)
            if key not in seen:
                seen.add(key)
                unique_pais.append(pai)
        return unique_pais

    @staticmethod
    def get_agari_pai(pais: List[Pai]) -> List[Pai]:
        agari_pai = Shoupai.get_agari_pai_regression(pais)
        agari_pai = Shoupai.remove_duplicates(agari_pai)
        agari_pai = Shoupai.sort_pai(agari_pai)
        return agari_pai

    @staticmethod
    def get_agari_pai_regression(pais: List[Pai]) -> List[Pai]:
        agari_pai: List[Pai] = []
        if len(pais) >= 4:
            sort_pai = Shoupai.sort_pai(pais)
            unique_pais = Shoupai.remove_duplicates(pais)
            unique_pais = Shoupai.sort_pai(unique_pais)

            for i in range(len(unique_pais) - 2):
                # 順子のチェック
                if Shoupai.is_shunzi(unique_pais[i : i + 3]):
                    new_pais: List[Pai] = pais.copy()
                    for p in unique_pais[i : i + 3]:
                        new_pais.remove(p)
                    agari_pai.extend(Shoupai.get_agari_pai_regression(new_pais))

            for i in range(len(pais) - 2):
                # カンツであればアガリ牌はない
                if (
                    len(pais) == 4
                    and (pais[0].num == pais[1].num == pais[2].num == pais[3].num)
                    and (pais[0].suit == pais[1].suit == pais[2].suit == pais[3].suit)
                ):
                    return agari_pai

                # 刻子のチェック
                if Shoupai.is_kezi(sort_pai[i : i + 3]):
                    new_pais = sort_pai[:i] + sort_pai[i + 3 :]
                    agari_pai.extend(Shoupai.get_agari_pai_regression(new_pais))

        elif len(pais) == 1:
            agari_pai.append(Pai(num=pais[0].num, suit=pais[0].suit))
            return agari_pai

        if len(pais) == 4:
            sort_pai = Shoupai.sort_pai(pais)
            if Shoupai.is_duizi(sort_pai[:2]):
                agari_pai.extend(Shoupai.get_mianzi_pai(sort_pai[2:]))

            if Shoupai.is_duizi(sort_pai[2:]):
                agari_pai.extend(Shoupai.get_mianzi_pai(sort_pai[:2]))

            return agari_pai

        return agari_pai

    def _check_regular(self) -> Tuple[bool, List[Pai]]:
        # メイン処理
        agari_hai = self.get_agari_pai(self.bingpai)
        is_tenpai = len(agari_hai) > 0

        return is_tenpai, agari_hai
    
    def do_hule(self):
        pass
