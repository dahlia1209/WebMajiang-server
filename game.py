import asyncio
import time
import math
import random
import re
from typing import List, Optional, Union
from ws_message import WsMessage
from connection_manager import manager
from models import Paipu
import json

class Game:
    def __init__(self, socks, callback, rule, title, timer):
        self._socks = socks
        self._callback = callback
        self._rule = rule
        self._title = title or ""
        self._timer = timer
        self._model = {
            "title": self._title.replace("\n", ": ネット対戦\n"),
            "player": [
                (
                    s["user"]["name"]
                    if s and "user" in s and "name" in s["user"]
                    else "(NOP)"
                )
                for s in socks
            ],
            "qijia": None,
            "defen": [],
            "player_id": [0, 1, 2, 3],
        }
        self._uid = [
            s["user"]["uid"] if s and "user" in s and "uid" in s["user"] else "(NOP)"
            for s in socks
        ]
        self._seq = 0
        self._time_allowed = []
        self._time_limit = [None]* 4
        self._timer_id = []
        self._players = [None] * 4
        self._status = None
        self._reply = [None] * 4
        self._timeout_id = None
        self._paipu = None
        self._speed = 3

    async def initialize(self):
        if not self._socks:
            return
        for s in self._socks:
            await self.connect(s)

    async def connect(self, sock):
        if not sock:
            return
        id = self._uid.index(sock["user"]["uid"])
        self._players[id] = sock["sock"]
        # sock.emit('START')  ここはmanager（ConnectionManagerインスタンス）を使ってemitする
        message = WsMessage(event_name="START")
        await manager.send_personal_message(
            message=message.model_dump_json(), websocket=self._players[id]
        )
        if self._seq:
            msg = {
                "kaiju": {
                    "id": id,
                    "rule": self._rule,
                    "title": self._model["title"],
                    "player": self._model["player"],
                    "qijia": self._model.get("qijia"),
                    "log": self._paipu.log if self._paipu else [],
                }
            }
            message = WsMessage(event_name="GAME", content=msg)
            # sock.emit('GAME', msg)
            await manager.send_personal_message(
                message=message.model_dump_json(), websocket=self._players[id]
            )

        # sock.on("GAME", lambda reply: self.reply(id, reply))
        # msg = {"players": [s.request.user if s else None for s in self._players]}
        msg = {
            "players": [s["user"] if s and "user" in s else None for s in self._players]
        }
        await self.notify_players("players", [msg] * 4)

    async def disconnect(self, sock):
        if not sock:
            return
        id = self._uid.index(sock["user"]["uid"])
        self._players[id] = None
        if not any(self._players):
            self.stop(self._callback)
        if not self._reply[id]:
            self.reply(id, {"seq": self._seq})
        msg = {"players": [s["user"] if s else None for s in self._players]}
        await self.notify_players("players", [msg] * 4)

    async def notify_players(self, type, msg):
        for l in range(4):
            id = self._model.get("player_id", [])[l]
            if self._players[id]:
                message = WsMessage(event_name="GAME", content=json.dumps(msg[l]))
                await manager.send_personal_message(
                    message=message.model_dump_json(), websocket=self._players[id]
                )
                # self._players[id].emit("GAME", msg[l])

    async def call_players(self, type, msg, timeout):
        timeout = (
            0 if self._speed == 0 else self._speed * 200 if timeout is None else timeout
        )
        self._status = type
        self._reply = [None] *4 
        self._seq += 1
        for l in range(4):
            id = self._model.get("player_id", [])[l]
            msg[l]["seq"] = self._seq
            self._time_limit[id] = None
            if self._players[id] and self._timer:
                msg[l]["timer"] = get_timer(
                    type, self._timer[0], self._time_allowed[id], self._timer[2]
                )
                if msg[l]["timer"]:
                    timer = sum(msg[l]["timer"]) * 1000 + 500
                    self._time_limit[id] = int(time.time() * 1000) + timer
                    self._timer_id[id] = asyncio.get_event_loop().call_later(
                        timer / 1000, lambda: self.reply(id, {"seq": self._seq})
                    )
            if self._players[id]:
                # self._players[id].emit("GAME", msg[l])
                message = WsMessage(event_name="GAME", content=json.dumps(msg[l]))
                await manager.send_personal_message(
                    message=message.model_dump_json(), websocket=self._players[id]
                )
            else:
                self._reply[id] = {}
        if type == "jieju":
            self._callback(self._paipu)
            return
        self._timeout_id =  asyncio.get_event_loop().call_later(
            timeout / 1000, lambda: asyncio.ensure_future(self.next())
        )

    async def reply(self, id, reply):
        if reply["seq"] != self._seq:
            return
        if self._reply[id]:
            return
        self._timer_id[id] = None
        if self._time_limit[id]:
            allowed = (self._time_limit[id] - int(time.time() * 1000)) / 1000
            if (
                not re.match(r"^(kaiju|hule|pingju)$", self._status)
                and self._time_allowed[id]
            ):
                self._time_allowed[id] = math.ceil(
                    min(max(allowed, 0), self._time_allowed[id])
                )
        self._reply[id] = reply
        if self._status == "jieju":
            if self._players[id]:
                self._players[id].remove_all_listeners("GAME")
                self._players[id].emit("END", self._paipu)
            return
        if len([x for x in self._reply if x]) < 4:
            return
        if not self._timeout_id:
            self._timeout_id = asyncio.get_event_loop().call_soon(
                lambda: asyncio.ensure_future(self.next())
            )

    async def say(self, name, l):
        msg = [{"say": {"l": l, "name": name}} for _ in range(4)]
        await self.notify_players("say", msg)

    def delay(self, callback, timeout):
        asyncio.get_event_loop().call_later(
            timeout / 1000, lambda: self._handle_delay(callback)
        )

    def _handle_delay(self, callback):
        try:
            callback()
        except Exception as e:
            print(e)
            self._timeout_id = None
            for s in self._players:
                if s:
                    s.emit("END")
            self._callback()

    async def next(self):
        try:
            super().next() 
        except Exception as e:
            print(e)
            self._timeout_id = None
            for s in self._players:
                if s:
                    message = WsMessage(event_name="END")
                    await manager.send_personal_message(
                        message=message.model_dump_json(), websocket=s
                    )
                    # s.emit("END")
            self._callback()

    def qipai(self, shan):
        if self._timer:
            self._time_allowed = [self._timer[1]] * 4
        super().qipai(shan)

    async def kaiju(self, qijia: Optional[int] = None):
        self._model["qijia"] = qijia if qijia is not None else random.randint(0, 3)
        self._max_jushu = 0 if self._rule["場数"] == 0 else self._rule["場数"] * 4 - 1

        _paipu = Paipu(
            title=self._model["title"],
            player=self._model["player"],
            qijia=self._model["qijia"],
            log=[],
            defen=self._model["defen"].copy(),
            point=[],
            rank=[],
        )

        messages = []
        for id in range(4):
            msg = {
                "kaiju": {
                    "id": id,
                    "rule": self._rule,
                    "title": _paipu.title,
                    "player": _paipu.player,
                    "qijia": _paipu.qijia,
                }
            }
            messages.append(msg)

        await self.call_players("kaiju", messages, 0)

        # _view.kaiju() に相当する処理が必要であればここに追加
        # 例: return {"message": "Game started"}

        return {"message": "Game started", "paipu": _paipu.model_dump()}


def get_timer(
    type: str,
    limit: Union[int, float],
    allowed: Union[int, float] = 0,
    wait: Optional[Union[int, float]] = None,
) -> Optional[List[Union[int, float]]]:
    if type == "jieju":
        return None
    if re.match(r"^(kaiju|hule|pingju)$", type):
        return [wait] if wait else None
    return [limit, allowed]
