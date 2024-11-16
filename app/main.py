from fastapi import FastAPI, WebSocket, WebSocketDisconnect,FastAPI
from .routers import users,websocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:4173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(websocket.router)
app.include_router(users.router)



@app.get("/")
async def root():
    return {"message": "Hello World"}

