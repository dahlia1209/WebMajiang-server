from typing import List, Literal
from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_azure_auth import B2CMultiTenantAuthorizationCodeBearer, user
from typing import Union, Optional
from pydantic import BaseModel, EmailStr
from jwt.algorithms import RSAAlgorithm
import logging
from game import Game, get_timer
from connection_manager import manager
from ws_message import WsMessage

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
    Security,
    Query,
    WebSocketException,
    Cookie,
)
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from azure_ad_verify_token import verify_jwt
from faker import Faker
import random


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    TENANT_NAME: str = ""
    APP_CLIENT_ID: str = ""
    APP_CLIENT_SECRET: str = ""
    OPENAPI_CLIENT_ID: str = ""
    AUTH_POLICY_NAME: str = ""
    SCOPE_DESCRIPTION: str = "user_impersonation"
    REDIRECT_URI: str = "http://localhost:8000/signin-oidc"
    APP_CLIENT_ID: str = ""
    AZURE_AD_ISSUER: str = ""
    AZURE_AD_JWKS_URI: str = ""

    @computed_field
    @property
    def SCOPE_NAME(self) -> str:
        return f"https://{self.TENANT_NAME}.onmicrosoft.com/{self.APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}"

    @computed_field
    @property
    def SCOPES(self) -> dict:
        return {self.SCOPE_NAME: self.SCOPE_DESCRIPTION}

    @computed_field
    @property
    def OPENID_CONFIG_URL(self) -> dict:
        return f"https://{self.TENANT_NAME}.b2clogin.com/{self.TENANT_NAME}.onmicrosoft.com/{self.AUTH_POLICY_NAME}/v2.0/.well-known/openid-configuration"

    @computed_field
    @property
    def OPENAPI_AUTHORIZATION_URL(self) -> dict:
        return f"https://{settings.TENANT_NAME}.b2clogin.com/{settings.TENANT_NAME}.onmicrosoft.com/{settings.AUTH_POLICY_NAME}/oauth2/v2.0/authorize"

    @computed_field
    @property
    def OPENAPI_TOKEN_URL(self) -> dict:
        return f"https://{settings.TENANT_NAME}.b2clogin.com/{settings.TENANT_NAME}.onmicrosoft.com/{settings.AUTH_POLICY_NAME}/oauth2/v2.0/token"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()

app = FastAPI(
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.OPENAPI_CLIENT_ID,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

azure_scheme = B2CMultiTenantAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    openid_config_url=settings.OPENID_CONFIG_URL,
    openapi_authorization_url=settings.OPENAPI_AUTHORIZATION_URL,
    openapi_token_url=settings.OPENAPI_TOKEN_URL,
    scopes=settings.SCOPES,
    validate_iss=False,
)


@app.get("/")
async def root(token: user.User = Depends(azure_scheme)):
    return {"message": "Hello World"}


class Token(BaseModel):
    sub: str
    name: Optional[str]
    emails: Optional[List[EmailStr]] = None
    tfp: str
    nonce: str
    scp: str
    azp: str
    ver: str
    iat: int
    aud: str
    exp: int
    iss: str
    nbf: int


async def verify_token(
    token: str,
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        verifed_jwt = Token(
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


class User(BaseModel):
    uid: str
    name: str

    @staticmethod
    def generate_fake_name(locale="ja_JP"):
        fake = Faker(locale)
        return fake.name()


def debug_log(*args):
    logging.debug(" ".join(map(str, args)))


async def send_room_info(room_no):
    if room_no not in ROOM:
        return

    room = ROOM[room_no]
    for uid in room["uids"]:
        user_info = USER.get(uid)
        if not user_info:
            continue

        sock = user_info.get("sock")
        if not sock:
            continue

        message = WsMessage(
            event_name="ROOM",
            content={
                "room_no": room_no,
                "user": [
                    {**USER[uid]["user"], "offline": USER[uid].get("sock") is None}
                    for uid in room["uids"]
                ],
            },
        )
        await manager.send_personal_message(
            websocket=sock,message=message.model_dump_json()
        )

    debug_log(
        room_no,
        [
            ("+ " if USER[uid].get("sock") else "- ") + USER[uid]["user"]["name"]
            for uid in room["uids"]
        ],
    )
    return

def get_room_no():
    MAX = 260000
    while True:
        n = random.randint(0, MAX - 1)
        room_no = chr(65 + (n // 10000)) + "{:04}".format(n % 10000)
        if room_no not in ROOM:
            return room_no

def get_socks(room_no: int) -> List:
    uids = [ROOM[room_no]['uids'][i] if i < len(ROOM[room_no]['uids']) else None for i in range(4)]
    socks = []
    
    user_data = {uid: {key: value for key, value in user.items() if key != 'sock'} for uid, user in USER.items()}
    # while len(socks) < 4:
        
    #     uid = uids.pop(int(random.random() * len(uids)))
    #     socks.append(USER[uid]['sock'] if uid else None)
    for key, value in USER.items():
        if value['room_no'] == room_no:
            socks.append({
                "user": value["user"],
                "sock": value["sock"]
            })
    while len(socks) < 4:
        socks.append(None)
    
    print("socks",socks)
    return socks

def status_log():
    # ステータスログのためのロジックを実装
    pass


ROOM = {}
USER = {}


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., alias="token"),
    verified_token: Token = Depends(verify_token),
):
    await manager.connect(websocket)
    user = User(
        uid=verified_token.sub, name=verified_token.name or User.generate_fake_name()
    )
    message = WsMessage(event_name="HELLO", content=user.model_dump())
    await manager.send_personal_message(
        message=message.model_dump_json(), websocket=websocket
    )
    if not user:
        await manager.disconnect(websocket)
        return
    debug_log(f"++ connect: {user.name}")
    if user.uid not in USER:
        USER[user.uid] = {"user": user.model_dump(), "sock": websocket}
    elif USER[user.uid].get("sock"):
        message = WsMessage(event_name="ERROR", content="既に接続済みです")
        await manager.send_personal_message(message=message, websocket=websocket)
        await manager.disconnect(websocket)
        return
    else:
        USER[user.uid]["sock"] = websocket
        room_no = USER[user.uid].get("room_no")
        if room_no in ROOM and "game" in ROOM[room_no]:
            ROOM[room_no]["game"].connect(websocket)
        else:
            await send_room_info(room_no)
    try:
        while True:
            data = await websocket.receive_text()
            message = WsMessage.model_validate_json(data)
            if message.event_name == "HELLO":
                await manager.send_personal_message(
                    message.model_dump_json(), websocket=websocket
                )
            elif message.event_name == "ROOM":
                if not user:
                    return

                uid = message.content.get("uid", None)
                room_no = message.content.get("room_no", None)
                if uid:
                    if room_no not in ROOM:
                        return
                    if uid == user.uid and ROOM[room_no]["uids"][0] == user.uid:
                        for uid in ROOM[room_no]["uids"]:
                            if USER[uid]["room_no"] == room_no:
                                del USER[uid]["room_no"]
                                if "sock" in USER[uid]:
                                    await USER[uid]["sock"].send_json(
                                        {"HELLO": USER[uid]["user"]}
                                    )
                                else:
                                    del USER[uid]
                        del ROOM[room_no]
                        debug_log(
                            "ROOM:",
                            [
                                f"{('* ' if ROOM[r].get('game') else '')}{r}"
                                for r in ROOM
                            ],
                        )
                    elif uid == user.uid or ROOM[room_no]["uids"][0] == user.uid:
                        if USER[uid]["room_no"] == room_no:
                            ROOM[room_no]["uids"] = [
                                u for u in ROOM[room_no]["uids"] if u != uid
                            ]
                            del USER[uid]["room_no"]
                            if "sock" in USER[uid]:
                                await USER[uid]["sock"].send_json(
                                    {"HELLO": USER[uid]["user"]}
                                )
                            else:
                                del USER[uid]
                            await send_room_info(room_no)
                elif user.uid in USER and "room_no" in USER[user.uid]:
                    message = WsMessage(event_name="ERROR", content="既に入室済みです")
                    await manager.send_personal_message(
                        message=message.model_dump_json(), websocket=websocket
                    )
                    await manager.disconnect()
                elif room_no:
                    if room_no in ROOM:
                        if len(ROOM[room_no]["uids"]) >= 4:
                            message = WsMessage(event_name="ERROR", content="満室です")
                            await manager.send_personal_message(
                                message=message.model_dump_json(), websocket=websocket
                            )
                            return
                        ROOM[room_no]["uids"].append(user.uid)
                        USER[user.uid]["room_no"] = room_no
                        await  send_room_info(room_no)
                    else:
                        message = WsMessage(
                            event_name="ERROR",
                            content=f"ルーム {room_no} は存在しません",
                        )
                        await manager.send_personal_message(
                            message=message.model_dump_json(), websocket=websocket
                        )
                else:
                    room_no = get_room_no()
                    ROOM[room_no] = {"uids": [user.uid]}
                    USER[user.uid]["room_no"] = room_no
                    debug_log(
                        "ROOM:",
                        [f"{('* ' if ROOM[r].get('game') else '')}{r}" for r in ROOM],
                    )
                    await send_room_info(room_no)
                    # sock.on("START", start_handler(sock, room_no))  定義すること！！！！

                status_log()
            elif message.event_name == "START":
                room_no=message.content.get("room_no")
                rule=message.content.get("rule")
                timer=message.content.get("timer")
                if room_no in ROOM and ROOM[room_no]['uids'][0] == user.uid:
                    if 'game' in ROOM[room_no]:
                        return
                    
                    async def callback(paipu):
                        for uid in ROOM[room_no]['uids']:
                            if 'sock' not in USER[uid]:
                                del USER[uid]
                            else:
                                del USER[uid]['room_no']
                        del ROOM[room_no]
                        debug_log('<< end:', room_no)
                        debug_log('ROOM:', ['* ' + str(rn) if 'game' in ROOM[rn] else str(rn) for rn in ROOM.keys()])
                        status_log()

                    print("get_socks(room_no)",get_socks(room_no))
                    ROOM[room_no]['game'] = Game(get_socks(room_no), callback, rule, None, timer)
                    await ROOM[room_no]['game'].initialize()
                    ROOM[room_no]['game'].speed = 2
                    await ROOM[room_no]['game'].kaiju()
                    debug_log('>> start:', room_no)
                    debug_log('ROOM:', ['* ' + str(rn) if 'game' in ROOM[rn] else str(rn) for rn in ROOM.keys()])
                    status_log()
                print(message)
                await manager.send_personal_message(
                    message.model_dump_json(), websocket=websocket
                )
            elif message.event_name == "GAME":
                def find_user_by_uid(socks,uid):
                    for s in socks:
                        if s and 'user' in s and s['user'].get('uid') == uid:
                            return s['user']
                        return None
                    
                room_no=message.content.get("room_no")
                reply=message.content.get("reply")
                
                if room_no not in ROOM or 'game' not in ROOM[room_no]:
                    return
                game=ROOM[room_no]['game']
                uid=message.content.get("uid",None)
                socks=get_socks(room_no)
                user=find_user_by_uid(socks,uid)
                if not user:
                    return
                game.reply(uid, reply)

    except WebSocketDisconnect as e:
        print("WebSocketDisconnect",e)
        manager.disconnect(websocket)
        
        message = {"time": "", "message": "Offline"}
        await manager.broadcast(json.dumps(message))


@app.post("/auth/")
async def auth(request: Request):
    return {"message": "/auth/"}


@app.post("/auth/hatena")
async def auth(request: Request):
    return {"message": "/auth/hatena"}


@app.post("/auth/google")
async def auth(request: Request):
    return {"message": "/auth/google"}
