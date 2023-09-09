import datetime

from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
templates = Jinja2Templates(directory="app/templates")
user_chats = dict()

@app.get("/log/{user_display_name}")
async def search(request:Request, user_display_name:str):
    """チャットログを表示"""
    # display name辞書にない場合は何も返さない
    if user_display_name not in user_chats:
        return "No users exist!"
    print(user_display_name, user_chats[user_display_name])
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "user_display_name": user_display_name,
            "chat_log": user_chats[user_display_name]
        }
    )

@app.get("/")
async def hello():
    """インデックスページ"""
    return {"text": "Hello world!"}

clients = {}
display_name_dict = {}
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    """チャットアプリのウェブソケット"""
    # 接続を確立
    await websocket.accept()
    key = websocket.headers.get('sec-websocket-key')
    clients[key] = websocket
    print(f"ID:{key} Connection Successfull!")
    # 接続が確立したときのメッセージを返す
    await websocket.send_text(f"ID:{key} Connection Successfull!")

   # keyに紐づくdisplay nameを登録する
    display_name = await websocket.receive_text()
    if display_name.split(":")[0] == "Register Display Name":
        display_name_dict[key] = display_name.split(":")[1]
    print(f"ID:{key}'s display name is {display_name_dict[key]}")

    loop = True
    while loop:
        try:
            # メッセージを受ける
            data = await websocket.receive_text()
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            print(f"{now} ID: {key} | User: {display_name_dict[key]} | Message: {data}")

            # save chat logs
            if display_name_dict[key] not in user_chats:
                user_chats[display_name_dict[key]] = []
            user_chats[display_name_dict[key]].append(f"{now} {data}")

            # send reseived messages to all clients
            for client in clients.values():
                await client.send_text(f"{now} | {display_name_dict[key]} | {data}")
        except:
            if key in clients:
                clients.pop(key)
            loop = False