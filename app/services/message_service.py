from app.schemas.message import MessageCreate
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
from app.core.database import redis, get_pg_session
from app.models.room import RoomMembership
from app.tasks.celery_tasks import send_notification
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from bson import ObjectId
from app.utils.validators import check_message_content

class MessageService:
    @staticmethod
    async def create_message(mongo_db: AsyncIOMotorDatabase, room_id: str, user_id: str, username: str, message_data: MessageCreate) -> dict:
        # Content filtering
        error = check_message_content(message_data.content)
        if error:
            raise ValueError(error)
        doc = {
            "room_id": room_id,
            "user_id": user_id,
            "username": username,
            "content": message_data.content,
            "message_type": message_data.message_type,
            "file_url": message_data.file_url,
            "reply_to": message_data.reply_to,
            "reactions": [],
            "edited": False,
            "edited_at": None,
            "created_at": datetime.utcnow(),
            "metadata": message_data.metadata or {},
        }
        result = await mongo_db.messages.insert_one(doc)
        doc["id"] = str(result.inserted_id)

        # Notify offline room members
        # Get DB session for RoomMembership
        async with get_pg_session() as session:
            result = await session.execute(
                select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.is_active == True)
            )
            members = result.scalars().all()
            for m in members:
                if str(m.user_id) == user_id:
                    continue
                online = await redis.get(f"user:{m.user_id}:online")
                if not online:
                    send_notification.delay(str(m.user_id), f"New message in room {room_id}")
        return doc

    @staticmethod
    async def get_messages(mongo_db: AsyncIOMotorDatabase, room_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
        cursor = mongo_db.messages.find({"room_id": room_id}).sort("created_at", -1).skip(skip).limit(limit)
        messages = []
        async for msg in cursor:
            msg["id"] = str(msg["_id"])
            messages.append(msg)
        return messages

    @staticmethod
    async def search_messages(mongo_db: AsyncIOMotorDatabase, room_id: str, query: str, skip: int = 0, limit: int = 50) -> list:
        # Ensure text index exists
        await mongo_db.messages.create_index([("content", "text")])
        cursor = mongo_db.messages.find({
            "$and": [
                {"room_id": room_id},
                {"$text": {"$search": query}}
            ]
        }, {"score": {"$meta": "textScore"}}).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)
        messages = []
        async for msg in cursor:
            msg["id"] = str(msg["_id"])
            messages.append(msg)
        return messages

    @staticmethod
    async def edit_message(mongo_db: AsyncIOMotorDatabase, message_id: str, user_id: str, content: str) -> dict:
        msg = await mongo_db.messages.find_one({"_id": ObjectId(message_id)})
        if not msg:
            return None
        if msg["user_id"] != user_id:
            return None
        update = {
            "$set": {
                "content": content,
                "edited": True,
                "edited_at": datetime.utcnow(),
            }
        }
        await mongo_db.messages.update_one({"_id": ObjectId(message_id)}, update)
        msg.update(update["$set"])
        return msg

    @staticmethod
    async def delete_message(mongo_db: AsyncIOMotorDatabase, message_id: str, user_id: str) -> bool:
        from bson import ObjectId
        msg = await mongo_db.messages.find_one({"_id": ObjectId(message_id)})
        if not msg:
            return False
        if msg["user_id"] == user_id:
            result = await mongo_db.messages.delete_one({"_id": ObjectId(message_id)})
            return result.deleted_count == 1
        # If not author, check if user is admin in the room
        async with get_pg_session() as session:
            result = await session.execute(
                select(RoomMembership).where(RoomMembership.room_id == msg["room_id"], RoomMembership.user_id == user_id, RoomMembership.role == "admin", RoomMembership.is_active == True)
            )
            admin = result.scalars().first()
            if admin:
                result = await mongo_db.messages.delete_one({"_id": ObjectId(message_id)})
                return result.deleted_count == 1
        return False

    @staticmethod
    async def add_reaction(mongo_db: AsyncIOMotorDatabase, message_id: str, user_id: str, emoji: str) -> dict:
        msg = await mongo_db.messages.find_one({"_id": ObjectId(message_id)})
        if not msg:
            return None
        # Remove any existing reaction by this user
        reactions = [r for r in msg.get("reactions", []) if r["user_id"] != user_id]
        reactions.append({"user_id": user_id, "emoji": emoji})
        update = {"$set": {"reactions": reactions}}
        await mongo_db.messages.update_one({"_id": ObjectId(message_id)}, update)
        msg["reactions"] = reactions
        return msg 