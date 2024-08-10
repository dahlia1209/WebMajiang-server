import logging
from manager.connection_manager import ConnectionManager, WsMessage
from manager.room_user_manager import RoomUserManager
from manager.settings_manager import Settings
import models.models as models
from routers import root
from dependencies import get_connection_manager, get_room_user_manager, get_settings
from services import majiang_service
from helpers.websocket_helpers import authenticate_and_manage_user, manage_game_room, notify_game_start


from majiang_core.game import Game


from fastapi import (
    FastAPI,
    Request,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
    Query,
    WebSocketException,
)
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from azure_ad_verify_token import verify_jwt

app = FastAPI(
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": get_settings().OPENAPI_CLIENT_ID,
    },
)

app.include_router(root.router, prefix="", tags=["root"])


async def verify_token(token: str, settings: Settings = Depends(get_settings)):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        verifed_jwt = models.Token(
            **verify_jwt(
                token=token,
                valid_audiences=[settings.APP_CLIENT_ID],
                issuer=settings.AZURE_AD_ISSUER,
                jwks_uri=settings.AZURE_AD_JWKS_URI,
                verify=True,
            )
        )
        return verifed_jwt

    except Exception as e:
        # 予期しないその他のエラーをキャッチ
        raise WebSocketException(
            code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, reason="Invalid token"
        )


def debug_log(*args):
    logging.debug(" ".join(map(str, args)))


def status_log():
    # ステータスログのためのロジックを実装
    pass


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., alias="token"),
    verified_token: models.Token = Depends(verify_token),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
    room_user_manager: RoomUserManager = Depends(get_room_user_manager),
):
    # 1. WebSocket接続の確立
    await connection_manager.connect(websocket)

    # 2. ユーザー認証と情報管理
    user = authenticate_and_manage_user(verified_token, websocket, room_user_manager)

    # 3. ゲームルームの管理
    room = manage_game_room(user, room_user_manager)

    # 4. ゲーム開始通知（必要な場合）
    print("room.users",room.users)
    if len(room.users) == 1:
        await notify_game_start(room, connection_manager, room_user_manager)
    

    try:
        while True:
            recieved_data = await websocket.receive_text()
            message = WsMessage.model_validate_json(recieved_data)
            print(message.model_dump_json())

            if message.event_name == "HELLO":
                await connection_manager.send_personal_message(
                    message=message, websocket=websocket
                )
            elif message.event_name == "GAME":
                room = room_user_manager.get_room(user_uid=verified_token.sub)
                if message.content["action"] == "game_info":
                    # room.game = Game.model_validate(message.content["game"])
                    # room.game.players[0].user = room_user_manager.get_user(
                    #     verified_token.sub
                    # )
                    pass
                elif message.content["action"] == "kaiju":
                    room.game = Game.model_validate(message.content["game"])
                    room.game.players[0].user = room_user_manager.get_user(
                        verified_token.sub
                    )
                    room.game.kaiju()
                    response = WsMessage(
                        event_name="GAME",
                        content={
                            "action": "call_players",
                            "param": {
                                "type": "kaiju",
                                "msg": room.game.msg,
                                "timeout": 0,
                            },
                            "update": {
                                "qijia": room.game.model.qijia,
                                "max_jushu": room.game.max_jushu,
                                "paipu": room.game.paipu,
                            },
                        },
                    )
                    room.game.reply = [None] * 4
                    await connection_manager.send_personal_message(
                        message=response, websocket=websocket
                    )
                elif message.content["action"] == "reply":
                    param = message.content.get("param")
                    if isinstance(param, dict):
                        room.game.reply[param.get("id")] = param.get("reply") or {}
                        room.game.reply_count += 1
                        print("room.game.reply_count", room.game.reply_count)
                    if room.game.reply_count == 4:
                        response = WsMessage(
                            event_name="GAME",
                            content={
                                "action": "next",
                                "update": {"reply": room.game.reply},
                            },
                        )
                        await connection_manager.send_personal_message(
                            message=response, websocket=websocket
                        )
                        room.game.reply_count = 0
                elif message.content["action"] == "qipai":
                    room.game.qipai()
                    response = WsMessage(
                        event_name="GAME",
                        content={
                            "action": "call_players",
                            "param": {
                                "type": "qipai",
                                "msg": room.game.msg,
                                "timeout": 0,
                            },
                            "update": {
                                "model": room.game.model,
                                "diyizimo": room.game.diyizimo,
                                "fengpai": room.game.fengpai,
                                "dapai": room.game.dapai_pai,
                                "gang": room.game.gang_pai,
                                "lizhi": room.game.lizhi,
                                "yifa": room.game.yifa,
                                "n_gang": room.game.n_gang,
                                "neng_rong": room.game.neng_rong,
                                "hule": room.game.hule_pai,
                                "hule_option": room.game.hule_option,
                                "no_game": room.game.no_game,
                                "lianzhuang": room.game.lianzhuang,
                                "changbang": room.game.changbang,
                                "fenpei": room.game.fenpei,
                                "defen": room.game.paipu.defen,
                                "log": room.game.paipu.log,
                            },
                        },
                    )
                    room.game.reply = [None] * 4
                    await connection_manager.send_personal_message(
                        message=response, websocket=websocket
                    )
                elif message.content["action"] == "zimo":
                    paipu = room.game.zimo()
                    response = WsMessage(
                        event_name="GAME",
                        content={
                            "action": "call_players",
                            "param": {
                                "type": "zimo",
                                "msg": room.game.msg,
                                "timeout": None,
                            },
                            "update": {
                                "model": {
                                    "lunban": room.game.model.lunban,
                                    "shoupai": [item.model_dump(by_alias=True) for item in room.game.model.shoupai],
                                    "shan": room.game.model.shan,
                                },
                                "paipu": room.game.paipu,
                                "view": paipu,
                            },
                        },
                    )
                    await connection_manager.send_personal_message(
                        message=response, websocket=websocket
                    )
                elif message.content["action"] == "dapai":
                    param = message.content.get("param")
                    if isinstance(param, dict):
                        dapai = param.get("dapai")
                        recieved_data = param.get("update")
                        room.game.model.update_shoupai(
                            recieved_data["model"]["shoupai"]
                        )
                        room.game.model.update_he(recieved_data["model"]["he"])
                        # room.game.model.update_shan(recieved_data["model"]["shan"])
                        room.game.model.lunban = recieved_data["model"]["lunban"]
                        update_val = room.game.dapai(dapai)
                        response = WsMessage(
                            event_name="GAME",
                            content={
                                "action": "call_players",
                                "param": {
                                    "type": "dapai",
                                    "msg": room.game.msg,
                                    "timeout": None,
                                },
                                "update": update_val,
                            },
                        )
                        await connection_manager.send_personal_message(
                            message=response, websocket=websocket
                        )
                elif message.content["action"] == "fulou":
                    param = message.content.get("param")
                    if isinstance(param, dict):
                        fulou = param.get("fulou")
                        update_val = await room.game.fulou(fulou)
                        response = WsMessage(
                            event_name="GAME",
                            content={
                                "action": "call_players",
                                "param": {
                                    "type": "fulou",
                                    "msg": room.game.msg,
                                    "timeout": None,
                                },
                                "update": update_val,
                            },
                        )
                        await connection_manager.send_personal_message(
                            message=response, websocket=websocket
                        )
                elif message.content["action"] == "hule":
                    param = message.content.get("param")
                    if isinstance(param, dict):
                        update_val = await room.game.hule()
                        response = WsMessage(
                            event_name="GAME",
                            content={
                                "action": "call_players",
                                "param": {
                                    "type": "hule",
                                    "msg": room.game.msg,
                                    "timeout": room.game.wait,
                                },
                                "update": update_val,
                            },
                        )
                        await connection_manager.send_personal_message(
                            message=response, websocket=websocket
                        )
                elif message.content["action"] == "gang":
                    param = message.content.get("param")
                    if isinstance(param, dict):
                        gang = param.get("gang")
                        update_val = await room.game.gang(gang)
                        response = WsMessage(
                            event_name="GAME",
                            content={
                                "action": "call_players",
                                "param": {
                                    "type": "fulou",
                                    "msg": room.game.msg,
                                    "timeout": None,
                                },
                                "update": update_val,
                            },
                        )
                        await connection_manager.send_personal_message(
                            message=response, websocket=websocket
                        )
                        
                        

    except WebSocketDisconnect as e:
        print("WebSocketDisconnect", e)
        connection_manager.disconnect(websocket)

        message = {"time": "", "message": "Offline"}
        await connection_manager.broadcast(json.dumps(message))


@app.post("/auth/")
async def auth(request: Request):
    return {"message": "/auth/"}


@app.post("/auth/hatena")
async def auth(request: Request):
    return {"message": "/auth/hatena"}


@app.post("/auth/google")
async def auth(request: Request):
    return {"message": "/auth/google"}
