from typing import List, Optional, Any
from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime
import random
import asyncio
from dependencies import get_connection_manager, ConnectionManager
from majiang_ui.board import Board as UIBoard
from fastapi import Depends
from majiang_core import game, player
from models.models import WsMessage


async def call_players(
    game: game.Game,
    type: Any,
    timeout: Optional[Any] = None,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    timeout = (
        0 if game.speed == 0 else (game.speed * 200 if timeout is None else timeout)
    )
    game.status = type
    game.reply = []

    for l in range(4):
        id = game.model.player_id[l]
        if game.sync:
            # await self.players[id].action(
            #     msg[l], lambda reply: self.reply(id, reply)
            # )
            if game.players[l].user is not None:
                message = WsMessage(
                    event_name="GAME",
                    content=game.msg[id],
                )
                await manager.send_personal_message(
                    message=message, websocket=game.players[id].user.client_socket
                )
        else:
            await asyncio.sleep(0)
            if game.players[id].user is not None:
                message = WsMessage(
                    event_name="GAME",
                    content={"action": "action", "msg": game.msg[id].model_dump(),"player_id":id},
                )
                await manager.send_personal_message(
                    message=message, websocket=game.players[id].user.client_socket
                )
            # await game.players[id].action(msg[l], lambda reply: game.reply(id, reply))

    # if not game.sync:
    #     game.timeout_id = asyncio.get_event_loop().call_later(timeout / 1000, game.next)
