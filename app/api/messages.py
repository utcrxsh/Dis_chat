from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService
from app.core.database import get_mongo_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_pg_session
from app.models.room import RoomMembership
from sqlalchemy.future import select
from typing import List, Optional
import os
from app.core.config import settings
from app.utils.rate_limiter import rate_limit
from datetime import datetime

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

async def require_room_membership(session: AsyncSession, room_id: str, user_id: str):
    result = await session.execute(
        select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.user_id == user_id)
    )
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    return membership

@router.post("/{room_id}", response_model=MessageResponse)
@rate_limit()
async def send_message(
    room_id: str,
    message_data: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
    session: AsyncSession = Depends(get_pg_session)
):
    await require_room_membership(session, room_id, str(current_user.id))
    try:
        msg = await MessageService.create_message(mongo_db, room_id, str(current_user.id), current_user.username, message_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return msg

@router.get("/{room_id}", response_model=List[MessageResponse])
async def get_messages(
    room_id: str,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
    session: AsyncSession = Depends(get_pg_session)
):
    await require_room_membership(session, room_id, str(current_user.id))
    if search:
        messages = await MessageService.search_messages(mongo_db, room_id, search, skip, limit)
    else:
        messages = await MessageService.get_messages(mongo_db, room_id, skip, limit)
    return messages

@router.put("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: str,
    content: str = Body(..., embed=True),
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
    session: AsyncSession = Depends(get_pg_session)
):
    # Find message and check room membership
    msg = await mongo_db.messages.find_one({"_id": message_id})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    await require_room_membership(session, msg["room_id"], str(current_user.id))
    updated = await MessageService.edit_message(mongo_db, message_id, str(current_user.id), content)
    if not updated:
        raise HTTPException(status_code=403, detail="Not allowed to edit this message")
    return updated

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
    session: AsyncSession = Depends(get_pg_session)
):
    msg = await mongo_db.messages.find_one({"_id": message_id})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    await require_room_membership(session, msg["room_id"], str(current_user.id))
    success = await MessageService.delete_message(mongo_db, message_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=403, detail="Not allowed to delete this message")
    return {"success": True}

@router.post("/{message_id}/react", response_model=MessageResponse)
async def add_reaction(
    message_id: str,
    emoji: str = Body(..., embed=True),
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
    session: AsyncSession = Depends(get_pg_session)
):
    msg = await mongo_db.messages.find_one({"_id": message_id})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    await require_room_membership(session, msg["room_id"], str(current_user.id))
    updated = await MessageService.add_reaction(mongo_db, message_id, str(current_user.id), emoji)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not add reaction")
    return updated

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    room_id: str = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_pg_session)
):
    await require_room_membership(session, room_id, str(current_user.id))
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.max_file_size:
        raise HTTPException(status_code=413, detail="File too large")
    # Validate file type (basic)
    allowed_types = ["image/png", "image/jpeg", "application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Unsupported file type")
    # Save file
    filename = f"{room_id}_{current_user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    file_url = f"/uploads/{filename}"
    return {"file_url": file_url}

@router.post("/{message_id}/report")
async def report_message(
    message_id: str,
    reason: str = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db)
):
    report = {
        "type": "message",
        "message_id": message_id,
        "reporter_id": str(current_user.id),
        "reason": reason,
        "created_at": datetime.utcnow()
    }
    await mongo_db.reports.insert_one(report)
    return {"success": True} 