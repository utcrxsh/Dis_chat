from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

class UserService:
    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    @staticmethod
    async def get_user(session: AsyncSession, user_id: str) -> Optional[User]:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def update_user(session: AsyncSession, user_id: str, update_data: UserUpdate) -> User:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return None
        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.password is not None:
            user.hashed_password = hash_password(update_data.password)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user_rooms(session: AsyncSession, user_id: str):
        # To be implemented
        return [] 