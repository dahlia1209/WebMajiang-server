from pydantic import BaseModel, Field
from typing import List, Optional, Any

class RuleConfig(BaseModel):
    配給原点: int
    順位点: List[str]
    連風牌は2符: bool
    赤牌: dict
    クイタンあり: bool
    喰い替え許可レベル: int
    場数: int
    途中流局あり: bool
    流し満貫あり: bool
    ノーテン宣言あり: bool
    ノーテン罰あり: bool
    最大同時和了数: int
    連荘方式: int
    トビ終了あり: bool
    オーラス止めあり: bool
    延長戦方式: int
    一発あり: bool
    裏ドラあり: bool
    カンドラあり: bool
    カン裏あり: bool
    カンドラ後乗せ: bool
    ツモ番なしリーチあり: bool
    リーチ後暗槓許可レベル: int
    役満の複合あり: bool
    ダブル役満あり: bool
    数え役満あり: bool
    役満パオあり: bool
    切り上げ満貫あり: bool