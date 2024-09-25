from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
import json
from typing import Dict
from fastapi.templating import Jinja2Templates

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]

    async def send_direct_message(self, sender_id: str, message: str, receiver_id: str):
        body = {
            'senderId': sender_id,
            'message': message
        }
        await self.active_connections[receiver_id].send_text(json.dumps(body))

app = FastAPI()
manager = ConnectionManager()
templates = Jinja2Templates(directory="templates")


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def get_chat_page(request: Request, user_id: str):
    return templates.TemplateResponse(
        request=request, name="chat.html", context={"user_id": user_id}
    )


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    await manager.connect(websocket, user_id)

    while True:
        data_json = await websocket.receive_text()
        data = json.loads(data_json)
        if data['type'] == 'heartbeat':
            print(f'Heartbeat: {user_id}')
            await manager.connect(websocket, user_id)
        elif data['type'] == 'message':
            await manager.send_direct_message(user_id, data['message'], data['receiverId'])
