from app.models.user import User
from app.models.room import Room, RoomMembership
from app.schemas.room import RoomCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import datetime
from typing import List

class RoomService:
    @staticmethod
    async def create_room(session: AsyncSession, room_data: RoomCreate, creator_id: UUID) -> Room:
        room = Room(
            name=room_data.name,
            description=room_data.description,
            is_private=room_data.is_private,
            created_by=creator_id
        )
        session.add(room)
        await session.flush()  # get room.id
        membership = RoomMembership(
            room_id=room.id,
            user_id=creator_id,
            joined_at=datetime.datetime.utcnow(),
            role="admin",
            is_active=True
        )
        session.add(membership)
        await session.commit()
        await session.refresh(room)
        return room

    @staticmethod
    async def join_room(session: AsyncSession, room_id: UUID, user_id: UUID) -> RoomMembership:
        # Check if already a member
        result = await session.execute(
            select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.user_id == user_id)
        )
        membership = result.scalars().first()
        if membership:
            return membership
        membership = RoomMembership(
            room_id=room_id,
            user_id=user_id,
            joined_at=datetime.datetime.utcnow(),
            role="member",
            is_active=True
        )
        session.add(membership)
        await session.commit()
        await session.refresh(membership)
        return membership

    @staticmethod
    async def get_room(*args, **kwargs):
        pass

    @staticmethod
    async def update_room(*args, **kwargs):
        pass

    @staticmethod
    async def leave_room(session: AsyncSession, room_id: UUID, user_id: UUID) -> bool:
        result = await session.execute(
            select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.user_id == user_id, RoomMembership.is_active == True)
        )
        membership = result.scalars().first()
        if not membership:
            return False
        membership.is_active = False
        await session.commit()
        return True

    @staticmethod
    async def get_user_rooms(session: AsyncSession, user_id: UUID) -> List[Room]:
        result = await session.execute(
            select(Room).join(RoomMembership).where(RoomMembership.user_id == user_id, RoomMembership.is_active == True)
        )
        return result.scalars().all()

    @staticmethod
    async def get_room_members(session: AsyncSession, room_id: UUID) -> List[User]:
        result = await session.execute(
            select(User).join(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.is_active == True)
        )
        return result.scalars().all()

    @staticmethod
    async def ban_user(session: AsyncSession, room_id: UUID, target_user_id: UUID, admin_user_id: UUID) -> bool:
        # Check if admin_user_id is admin in the room
        from app.models.room import RoomMembership
        from sqlalchemy.future import select
        result = await session.execute(
            select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.user_id == admin_user_id, RoomMembership.role == "admin", RoomMembership.is_active == True)
        )
        admin = result.scalars().first()
        if not admin:
            return False
        # Ban the target user
        result = await session.execute(
            select(RoomMembership).where(RoomMembership.room_id == room_id, RoomMembership.user_id == target_user_id, RoomMembership.is_active == True)
        )
        membership = result.scalars().first()
        if not membership:
            return False
        membership.is_active = False
        await session.commit()
        return True 