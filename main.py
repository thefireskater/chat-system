from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]

    async def send_direct_message(self, message: str, user_id: str):
        await self.active_connections[user_id].send_text(message)

app = FastAPI()
manager = ConnectionManager()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label for="receiverId">Receiver ID</label>
            <input type="text" id="receiverId" autocomplete="off"/>
            <label for="messageText">Message</label>
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/{user_id}");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var receiverId = document.getElementById("receiverId")
                var messageText = document.getElementById("messageText")
                ws.send(JSON.stringify({"type": "message", "receiverId": receiverId.value, "message": messageText.value}))
                messageText.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/user/{user_id}")
async def get(user_id: str):
    # todo not secure, use jinja2 template
    return HTMLResponse(html.replace("{user_id}", user_id))


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
            await manager.send_direct_message(data['message'], data['receiverId'])
