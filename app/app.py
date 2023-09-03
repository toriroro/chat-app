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
templates = Jinja2Templates(directory="templates")

chat_log = list()
user_chats = dict()
@app.get("/home")
async def search(request: Request):
    """チャットログを表示"""
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "chat_log": chat_log
        }
    )

clients = {}
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """チャットアプリのウェブソケット"""
    await websocket.accept()
    key = websocket.headers.get('sec-websocket-key')
    clients[key] = websocket
    print(f"ID:{key} Connection Successfull!")
    await websocket.send_text(f"ID:{key} Connection Successfull!")
    while True:
        data = await websocket.receive_text()
        print(f"ID: {key} | Message: {data}")
        chat_log.append(f"ID: {key} | Message: {data}")
        if key not in user_chats:
            user_chats[key] = []
        user_chats[key].append(data)
        for client in clients.values():
            await client.send_text(f"ID: {key} | Message: {data}")