from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_mongo_db
from app.core.database import get_pg_session
from app.schemas.room import RoomCreate, RoomResponse, RoomMembershipResponse
from app.services.room_service import RoomService
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from uuid import UUID
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user)
):
    room = await RoomService.create_room(session, room_data, current_user.id)
    return room

@router.get("/", response_model=List[RoomResponse])
async def get_user_rooms(
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user)
):
    rooms = await RoomService.get_user_rooms(session, current_user.id)
    return rooms

@router.get("/{room_id}")
async def get_room(room_id: str):
    pass

@router.post("/{room_id}/join", response_model=RoomMembershipResponse)
async def join_room(
    room_id: UUID,
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user)
):
    membership = await RoomService.join_room(session, room_id, current_user.id)
    return membership

@router.delete("/{room_id}/leave")
async def leave_room(
    room_id: UUID,
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user)
):
    result = await RoomService.leave_room(session, room_id, current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Not a member of this room")
    return {"success": True}

@router.get("/{room_id}/members", response_model=List[UserResponse])
async def get_room_members(
    room_id: UUID,
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user)
):
    members = await RoomService.get_room_members(session, room_id)
    return members 

@router.post("/{room_id}/ban/{user_id}")
async def ban_user(
    room_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user)
):
    success = await RoomService.ban_user(session, room_id, user_id, current_user.id)
    if not success:
        raise HTTPException(status_code=403, detail="Not allowed or user not found")
    return {"success": True} 

@router.get("/{room_id}/reports")
async def get_room_reports(
    room_id: UUID,
    session: AsyncSession = Depends(get_pg_session),
    current_user: UserResponse = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db)
):
    # Check admin
    from app.models.room import RoomMembership
    from sqlalchemy.future import select
    result = await session.execute(
        select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.user_id == current_user.id, RoomMembership.role == "admin", RoomMembership.is_active == True)
    )
    admin = result.scalars().first()
    if not admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    # Get reports
    reports = []
    async for r in mongo_db.reports.find({"$or": [{"type": "message", "room_id": str(room_id)}, {"type": "user", "room_id": str(room_id)}]}):
        r["id"] = str(r["_id"])
        reports.append(r)
    return reports 