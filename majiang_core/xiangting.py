from typing import List, Dict, Union, Optional,Tuple,Callable
from pydantic import BaseModel, Field, field_validator, AliasChoices
from .shoupai import Shoupai
import math

def _xiangting(m: int, d: int, g: int, j: bool) -> int:
    n = 4 if j else 5
    if m > 4:
        d += m - 4
        m = 4
    if m + d > 4:
        g += (m + d) - 4
        d = 4 - m
    if m + d + g > n:
        g = n - (m + d)
    if j:
        d += 1
    return 13 - (m * 3) - (d * 2) - g

def dazi(bingpai: List[int]) -> Tuple[List[int], List[int]]:
    n_pai = 0
    n_dazi = 0
    n_guli = 0

    for n in range(1, 10):
        n_pai += bingpai[n]
        if n <= 7 and bingpai[n + 1] == 0 and bingpai[n + 2] == 0:
            n_dazi += n_pai // 2
            n_guli += n_pai % 2
            n_pai = 0

    n_dazi += n_pai // 2
    n_guli += n_pai % 2

    return [0, n_dazi, n_guli], [0, n_dazi, n_guli]

def mianzi(bingpai: List[int], n: int = 1) -> Tuple[List[int], List[int]]:
    if n > 9:
        return dazi(bingpai)

    max_a, max_b = mianzi(bingpai, n + 1)

    if n <= 7 and bingpai[n] > 0 and bingpai[n + 1] > 0 and bingpai[n + 2] > 0:
        bingpai[n] -= 1
        bingpai[n + 1] -= 1
        bingpai[n + 2] -= 1
        r_a, r_b = mianzi(bingpai, n)
        bingpai[n] += 1
        bingpai[n + 1] += 1
        bingpai[n + 2] += 1
        r_a[0] += 1
        r_b[0] += 1
        if r_a[2] < max_a[2] or (r_a[2] == max_a[2] and r_a[1] < max_a[1]):
            max_a = r_a
        if r_b[0] > max_b[0] or (r_b[0] == max_b[0] and r_b[1] > max_b[1]):
            max_b = r_b

    if bingpai[n] >= 3:
        bingpai[n] -= 3
        r_a, r_b = mianzi(bingpai, n)
        bingpai[n] += 3
        r_a[0] += 1
        r_b[0] += 1
        if r_a[2] < max_a[2] or (r_a[2] == max_a[2] and r_a[1] < max_a[1]):
            max_a = r_a
        if r_b[0] > max_b[0] or (r_b[0] == max_b[0] and r_b[1] > max_b[1]):
            max_b = r_b

    return max_a, max_b

def mianzi_all(shoupai: Shoupai, jiangpai: bool) -> int:
    r = {
        'm': mianzi(shoupai.bingpai.m),
        'p': mianzi(shoupai.bingpai.p),
        's': mianzi(shoupai.bingpai.s),
    }

    z = [0, 0, 0]
    for n in range(1, 8):
        if shoupai.bingpai.z[n] >= 3:
            z[0] += 1
        elif shoupai.bingpai.z[n] == 2:
            z[1] += 1
        elif shoupai.bingpai.z[n] == 1:
            z[2] += 1

    n_fulou = len(shoupai.fulou_pai)

    min_xiangting = 13

    for m in [r['m'][0], r['m'][1]]:
        for p in [r['p'][0], r['p'][1]]:
            for s in [r['s'][0], r['s'][1]]:
                x = [n_fulou, 0, 0]
                for i in range(3):
                    x[i] += m[i] + p[i] + s[i] + z[i]
                n_xiangting = _xiangting(x[0], x[1], x[2], jiangpai)
                if n_xiangting < min_xiangting:
                    min_xiangting = n_xiangting

    return min_xiangting


def xiangting_yiban(shoupai: Shoupai) -> int:
    min_xiangting = mianzi_all(shoupai, None)

    suits = ['m', 'p', 's', 'z']
    for s in suits:
        bingpai = shoupai.bingpai[s]
        for n in range(1, len(bingpai)):
            if bingpai[n] >= 2:
                bingpai[n] -= 2
                n_xiangting = mianzi_all(shoupai, True)
                bingpai[n] += 2
                if n_xiangting < min_xiangting:
                    min_xiangting = n_xiangting

    if min_xiangting == -1 and shoupai.zimo and len(shoupai.zimo) > 2:
        return 0

    return min_xiangting

def xiangting_guoshi(shoupai: Shoupai) -> int:
    if len(shoupai.fulou_pai) > 0:
        return math.inf

    n_yaojiu = 0
    n_duizi = 0

    suits = ['m', 'p', 's', 'z']
    yaojiu_tiles = {
        'm': [1, 9],
        'p': [1, 9],
        's': [1, 9],
        'z': [1, 2, 3, 4, 5, 6, 7]
    }

    for s in suits:
        bingpai = shoupai.bingpai[s]
        nn = yaojiu_tiles[s]
        for n in nn:
            if bingpai[n] >= 1:
                n_yaojiu += 1
            if bingpai[n] >= 2:
                n_duizi += 1

    return 12 - n_yaojiu if n_duizi > 0 else 13 - n_yaojiu

def xiangting_qidui(shoupai: Shoupai) -> int:
    if len(shoupai.fulou_pai) > 0:
        return math.inf

    n_duizi = 0
    n_guli = 0

    suits = ['m', 'p', 's', 'z']

    for s in suits:
        bingpai = shoupai.bingpai[s]
        for n in range(1, len(bingpai)):
            if bingpai[n] >= 2:
                n_duizi += 1
            elif bingpai[n] == 1:
                n_guli += 1

    if n_duizi > 7:
        n_duizi = 7
    if n_duizi + n_guli > 7:
        n_guli = 7 - n_duizi

    return 13 - n_duizi * 2 - n_guli

def xiangting(shoupai: Shoupai) -> int:
    return min(
        xiangting_yiban(shoupai),
        xiangting_guoshi(shoupai),
        xiangting_qidui(shoupai)
    )

def tingpai(shoupai: Shoupai, f_xiangting: Callable[[Shoupai], int] = xiangting) -> Optional[List[str]]:
    if shoupai.zimo:
        return None

    pai = []
    n_xiangting = f_xiangting(shoupai)
    suits = ['m', 'p', 's', 'z']

    for s in suits:
        bingpai = shoupai.bingpai[s]
        for n in range(1, len(bingpai)):
            if bingpai[n] >= 4:
                continue
            bingpai[n] += 1
            if f_xiangting(shoupai) < n_xiangting:
                pai.append(f"{s}{n}")
            bingpai[n] -= 1

    return pai