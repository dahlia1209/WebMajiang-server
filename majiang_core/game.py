from typing import List, Optional, Any
from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime
from .board import Board, Kaiju
from .rule import RuleConfig
import random
import copy
import json
import re
from .player import Player, Msg
from .shan import Shan
from .shoupai import Shoupai
from .he import He
from . import xiangting
from .hule import hule

# from connection_manager import ConnectionManager,WsMessage
from majiang_ui.board import Board as UIBoard


class Paipu(BaseModel):
    title: str
    player: List[str]
    qijia: int
    log: List[dict] = []
    defen: List[int]
    point: List[int] = []
    rank: List[int] = []


class Game(BaseModel):
    players: List[Player] = Field(alias="_players")
    callback: Optional[Any] = (
        Field(default_factory=lambda: lambda: None, alias="_callback"),
    )
    rule: RuleConfig = Field(default_factory=RuleConfig, alias="_rule")
    model: Board = Field(default_factory=Board, alias="_model")
    view: Optional[UIBoard] = Field(default=None, alias="_view")
    status: Optional[Any] = Field(default=None, alias="_status")
    reply: List[Any] = Field(default_factory=list, alias="_reply")
    reply_count: int = Field(default=0)
    sync: bool = Field(default=False, alias="_sync")
    stop: Optional[Any] = Field(default=None, alias="_stop")
    speed: int = Field(default=3, alias="_speed")
    wait: int = Field(default=0, alias="_wait")
    timeout_id: Optional[Any] = Field(default=None, alias="_timeout_id")
    handler: Any = Field(default=None, alias="_handler")
    msg: List[Msg] = []
    max_jushu: int = Field(default=0)
    paipu: Paipu = Field(default=None)
    diyizimo: bool = Field(default=False, alias="_diyizimo")
    fengpai: bool = Field(default=False, alias="_fengpai")
    dapai_pai: Any = Field(default=None, alias="_dapai")
    gang_pai: Any = Field(default=None, alias="_gang")
    lizhi: List[int] = Field(default=([0] * 4), alias="_lizhi")
    yifa: List[int] = Field(default=([0] * 4), alias="_yifa")
    n_gang: List[int] = Field(default=([0] * 4), alias="_n_gang")
    neng_rong: List[int] = Field(default=([1] * 4), alias="_neng_rong")
    hule_pai: List[Any] = Field(default=[], alias="_hule")
    hule_option: Any = Field(default=None, alias="_hule_option")
    no_game: bool = Field(default=False, alias="_no_game")
    lianzhuang: bool = Field(default=False, alias="_lianzhuang")
    changbang: int = Field(default=0, alias="_changbang")
    fenpei: Any = Field(default=None, alias="_fenpei")

    def __init__(self, **data):
        super().__init__(**data)
        kaiju = Kaiju(
            title=data.get("title") or "電脳麻将\n" + self.current_time(),
            player=["私", "下家", "対面", "上家"],
            qijia=0,
            zhuangfeng=0,
            jushu=0,
            changbang=0,
            lizhibang=0,
            defen=[self.rule.配給原点 for _ in range(4)],
            shan=None,
            shoupai=[],
            he=[],
            player_id=[0, 1, 2, 3],
        )
        self.model.kaiju(kaiju)

    @staticmethod
    def current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_paipu(self, paipu: Any):
        self.paipu.log[-1].append(paipu)

    def kaiju(self, qijia: Optional[int] = None):
        self.model.qijia = qijia if qijia is not None else random.randint(0, 3)

        self.max_jushu = 0 if self.rule.場数 == 0 else self.rule.場数 * 4 - 1

        # self.paipu = {
        #     "title": self.model.title,
        #     "player": self.model.player,
        #     "qijia": self.model.qijia,
        #     "log": [],
        #     "defen": self.model.defen.copy(),
        #     "point": [],
        #     "rank": [],
        # }

        self.paipu = Paipu(
            title=self.model.title,
            player=self.model.player,
            qijia=self.model.qijia,
            defen=self.model.defen.copy(),
        )

        for id in range(4):
            kaiju = Kaiju(
                id=id,
                rule=self.rule,
                title=self.model.title,
                player=self.model.player,
                qijia=self.model.qijia,
            )
            self.msg.append(Msg(kaiju=kaiju))

        # self.call_players("kaiju", self.msg, 0)

        # if self.view:
        #     self.view.kaiju()

    def qipai(self, shan: Shan = None):
        # model=self.model
        self.model.shan = shan or Shan(self.rule)

        for l in range(4):
            qipai = [self.model.shan.zimo() for _ in range(13)]
            self.model.shoupai[l] = Shoupai(qipai)
            self.model.he[l] = He()
            self.model.player_id[l] = (self.model.qijia + self.model.jushu + l) % 4

        self.model.lunban = -1
        self.diyizimo = True
        self.fengpai = self.rule.途中流局あり or False
        self.dapai_pai = None
        self.gang_pai = None
        self.lizhi = [0] * 4
        self.yifa = [0] * 4
        self.n_gang = [0] * 4
        self.neng_rong = [1] * 4
        self.hule_pai = []
        self.hule_option = None
        self.no_game = False
        self.lianzhuang = False
        self.changbang = self.model.changbang
        self.fenpei = None

        self.paipu.defen = self.model.defen.copy()
        self.paipu.log.append([])

        paipu = {
            "qipai": {
                "zhuangfeng": self.model.zhuangfeng,
                "jushu": self.model.jushu,
                "changbang": self.model.changbang,
                "lizhibang": self.model.lizhibang,
                "defen": [self.model.defen[id] for id in self.model.player_id],
                "baopai": self.model.shan.baopai[0],
                "shoupai": [shoupai.to_string() for shoupai in self.model.shoupai],
            }
        }
        self.add_paipu(paipu)

        self.msg = [copy.deepcopy(paipu) for _ in range(4)]
        for l in range(4):
            for i in range(4):
                if i != l:
                    self.msg[l]["qipai"]["shoupai"][i] = ""

    def zimo(self):
        self.model.lunban = (self.model.lunban + 1) % 4

        zimo_tile = self.model.shan.zimo()
        self.model.shoupai[self.model.lunban].zimo(zimo_tile)

        paipu = {"zimo": {"l": self.model.lunban, "p": zimo_tile}}
        self.add_paipu(paipu)

        self.msg = []
        for l in range(4):
            msg_l = json.loads(json.dumps(paipu))
            if l != self.model.lunban:
                msg_l["zimo"]["p"] = ""
            self.msg.append(msg_l)

        return paipu

    def dapai(self, dapai: str):
        update_val = {}
        self.yifa[self.model.lunban] = 0
        update_val.update({"yifa": self.yifa})

        if not self.model.shoupai[self.model.lunban].lizhi:
            self.neng_rong[self.model.lunban] = True
            update_val.update({"neng_rong": self.neng_rong})

        self.model.shoupai[self.model.lunban].dapai(dapai)
        self.model.he[self.model.lunban].dapai(dapai)
        update_val.update(
            {"model": {"shoupai": [item.model_dump(by_alias=True) for item in self.model.shoupai], "he": self.model.he}}
        )

        if self.diyizimo:
            if not dapai.startswith("z") or dapai[1] not in "1234":
                self.fengpai = False
                update_val.update({"fengpai": self.fengpai})
            if self.dapai_pai and self.dapai_pai[:2] != dapai[:2]:
                self.fengpai = False
                update_val.update({"fengpai": self.fengpai})
        else:
            self.fengpai = False
            update_val.update({"fengpai": self.fengpai})

        if dapai.endswith("*"):
            self.lizhi[self.model.lunban] = 2 if self.diyizimo else 1
            update_val.update({"lizhi": self.lizhi})
            self.yifa[self.model.lunban] = self.rule["一発あり"]
            update_val.update({"yifa": self.yifa})

        shoupai = self.model.shoupai[self.model.lunban]
        tingpai = xiangting.tingpai(shoupai)

        if (
            xiangting.xiangting(shoupai) == 0
            and tingpai
            and any(p in self.model.he[self.model.lunban] for p in tingpai)
        ):
            self.neng_rong[self.model.lunban] = False
            update_val.update({"neng_rong": self.neng_rong})

        self.dapai_pai = dapai
        update_val.update({"dapai_pai": self.dapai_pai})

        paipu = {"dapai": {"l": self.model.lunban, "p": dapai}}
        self.add_paipu(paipu)
        update_val.update({"paipu": self.paipu})
        update_val.update({"view": paipu})

        if self.gang_pai:
            self.kaigang()  ## TODO!!!!

        self.msg = [json.loads(json.dumps(paipu)) for _ in range(4)]

        return update_val

    async def fulou(self, fulou: str):
        update_val = {}
        self.diyizimo = False
        self.yifa = [0, 0, 0, 0]
        update_val.update({"diyizimo": self.diyizimo, "yifa": self.yifa})

        self.model.he[self.model.lunban].fulou(fulou)

        d = re.search(r"[\+\=\-]", fulou)
        if d:
            self.model.lunban = (self.model.lunban + "_-=+".index(d.group())) % 4

        self.model.shoupai[self.model.lunban].fulou(fulou)
        update_val.update(
            {
                "model": {
                    "shoupai": [item.model_dump(by_alias=True) for item in self.model.shoupai],
                    "he": self.model.he,
                    "lunban": self.model.lunban,
                }
            }
        )

        if re.match(r"^[mpsz]\d{4}", fulou):
            self.gang_pai = fulou
            self.n_gang[self.model.lunban] += 1
            update_val.update({"gang": self.gang_pai, "n_gang": self.n_gang})

        paipu = {"fulou": {"l": self.model.lunban, "m": fulou}}
        self.add_paipu(paipu)
        update_val.update({"paipu": self.paipu})
        update_val.update({"view": paipu})

        self.msg = [json.loads(json.dumps(paipu)) for _ in range(4)]

        return update_val
    
    def hule(self):
        update_val = {}
        model = self.model

        if self.status != 'hule':
            model.shan.close()
            self.hule_option = 'qianggang' if self.status == 'gang' else 'lingshang' if self.status == 'gangzimo' else None
        update_val.update({"hule_option": self.hule_option})

        menfeng = self.hule_pai.pop(0) if self.hule_pai else model.lunban
        update_val.update({"hule_pai": self.hule_pai})
        rongpai = None if menfeng == model.lunban else (
            (self.gang_pai[0] + self.gang_pai[-1]) if self.hule_option == 'qianggang'
            else self.dapai[:2]
        ) + '_+=-'[(4 + model.lunban - menfeng) % 4]
        shoupai = model.shoupai[menfeng].clone() 
        fubaopai = model.shan.fubaopai if shoupai.lizhi else None
        param = {
            'rule': self.rule,
            'zhuangfeng': model.zhuangfeng,
            'menfeng': menfeng,
            'hupai': {
                'lizhi': self.lizhi[menfeng],
                'yifa': self.yifa[menfeng],
                'qianggang': self.hule_option == 'qianggang',
                'lingshang': self.hule_option == 'lingshang',
                'haidi': 0 if model.shan.paishu > 0 or self.hule_option == 'lingshang'
                        else 1 if not rongpai else 2,
                'tianhu': 0 if not (self.diyizimo and not rongpai)
                        else 1 if menfeng == 0 else 2
            },
            'baopai': model.shan.baopai,
            'fubaopai': fubaopai,
            'jicun': {
                'changbang': model.changbang,
                'lizhibang': model.lizhibang
            }
        }
        hule_result = hule(shoupai, rongpai, param)

        if self.rule.連荘方式 > 0 and menfeng == 0:
            self.lianzhuang = True
        if self.rule.場数 == 0:
            self.lianzhuang = False
        if hule_result:
            self.fenpei = hule_result.fenpei

        paipu = {
            'hule': {
                'l': menfeng,
                'shoupai': shoupai.zimo(rongpai).toString() if rongpai else shoupai.toString(),
                'baojia': model.lunban if rongpai else None,
                'fubaopai': fubaopai,
                'fu': hule_result.fu,
                'fanshu': hule_result.fanshu,
                'damanguan': hule_result.damanguan,
                'defen': hule_result.defen,
                'hupai': hule_result.hupai,
                'fenpei': hule_result.fenpei
            }
        }
        update_val.update({"paipu": paipu})
        for key in ['fu', 'fanshu', 'damanguan']:
            if not paipu['hule'][key]:
                del paipu['hule'][key]
        self.add_paipu(paipu)

        msg = [None] * 4
        for l in range(4):
            msg[l] = json.loads(json.dumps(paipu))
        self.msg =msg
        # self.call_players('hule', msg, self._wait)

        # if self._view:
        #     self._view.update(paipu)
        
        return update_val
        
    def gang(self, gang):
        update_val = {}
        model = self.model

        model.shoupai[model.lunban].gang(m=gang)
        update_val.update({"shoupai": model.shoupai})

        paipu = {"gang": {"l": model.lunban, "m": gang}}
        update_val.update({"paipu": paipu})
        self.add_paipu(paipu)

        if self.gang_pai:
            self.kaigang()

        self.gang_pai = gang
        self.n_gang[model.lunban] += 1
        update_val.update({"gang_pai": self.paipu})
        update_val.update({"n_gang": self.n_gang})

        msg = []
        for l in range(4):
            msg.append(paipu.copy()) 
        self.msg =msg

        # self.call_players('gang', msg, None)

        # if self._view:
        #     self._view.update(paipu)
        return update_val

    def kaigang(self):
        self.gang_pai = None

        if not self.rule.カンドラあり:
            return

        model = self.model

        model.shan.kaigang()
        baopai = model.shan.baopai.pop()

        paipu = {"kaigang": {"baopai": baopai}}
        self.add_paipu(paipu)

        msg = []
        for _ in range(4):
            msg.append(copy.deepcopy(paipu))
        
        # self.notify_players('kaigang', msg)

        # if self._view:
        #     self._view.update(paipu)