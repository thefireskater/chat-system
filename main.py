from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
import json
from typing import Dict
from fastapi.templating import Jinja2Templates
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected")

    async def send_direct_message(self, sender_id: str, message: str, receiver_id: str):
        body = {
            'senderId': sender_id,
            'message': message
        }
        await self.active_connections[receiver_id].send_text(json.dumps(body))
        logger.info(f"Message sent from {sender_id} to {receiver_id}")

app = FastAPI()
manager = ConnectionManager()
templates = Jinja2Templates(directory="templates")


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def get_chat_page(request: Request, user_id: str):
    logger.info(f"Chat page requested for user {user_id}")
    return templates.TemplateResponse(
        request=request, name="chat.html", context={"user_id": user_id}
    )


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    await manager.connect(websocket, user_id)
    logger.info(f"WebSocket connection established for user {user_id}")

    try:
        while True:
            data_json = await websocket.receive_text()
            data = json.loads(data_json)
            if data['type'] == 'heartbeat':
                logger.debug(f'Heartbeat received from user: {user_id}')
                await manager.connect(websocket, user_id)
            elif data['type'] == 'message':
                await manager.send_direct_message(user_id, data['message'], data['receiverId'])
    except Exception as e:
        logger.error(f"Error in WebSocket connection for user {user_id}: {str(e)}")
    finally:
        manager.disconnect(user_id)
