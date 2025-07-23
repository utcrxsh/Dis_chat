from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from typing import Dict, List
from app.core.security import decode_access_token
from app.services.room_service import RoomService
from app.core.database import get_pg_session
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.services.message_service import MessageService
from app.schemas.message import MessageCreate, MessageResponse
from app.core.database import get_mongo_db
from app.schemas.user import UserResponse
from app.core.database import redis
from app.utils.rate_limiter import rate_limiter

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        self.active_connections.setdefault(room_id, []).append(websocket)
        self.user_connections[user_id] = websocket

    async def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def broadcast_to_room(self, message: dict, room_id: str):
        for ws in self.active_connections.get(room_id, []):
            await ws.send_json(message)

    async def send_personal_message(self, message: dict, user_id: str):
        ws = self.user_connections.get(user_id)
        if ws:
            await ws.send_json(message)

manager = ConnectionManager()

async def get_connection_manager():
    return manager

async def set_user_online(user_id: str):
    await redis.set(f"user:{user_id}:online", 1, ex=60)

async def set_user_offline(user_id: str):
    await redis.delete(f"user:{user_id}:online")

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
    manager: ConnectionManager = Depends(get_connection_manager),
    session: AsyncSession = Depends(get_pg_session),
    mongo_db=Depends(get_mongo_db)
):
    # Authenticate user from token
    payload = decode_access_token(token)
    if not payload or "sub" not in payload or "username" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = payload["sub"]
    username = payload["username"]
    # Check room membership
    is_member = await RoomService.join_room(session, UUID(room_id), UUID(user_id))
    if not is_member:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(websocket, room_id, user_id)
    await set_user_online(user_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Rate limiting
            allowed = await rate_limiter.is_allowed(user_id)
            if not allowed:
                await websocket.send_json({"error": "Rate limit exceeded"})
                continue
            # Validate and save message
            try:
                msg_in = MessageCreate(**data)
            except Exception as e:
                await websocket.send_json({"error": "Invalid message format", "details": str(e)})
                continue
            saved = await MessageService.create_message(mongo_db, room_id, user_id, username, msg_in)
            await manager.broadcast_to_room(saved, room_id)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, room_id, user_id)
        await set_user_offline(user_id) 