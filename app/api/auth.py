from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_pg_session
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.user_service import UserService
from app.core.security import create_access_token
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_pg_session)):
    try:
        user = await UserService.create_user(session, user_data)
        return user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")

@router.post("/login", response_model=Token)
async def login(form_data: UserCreate, session: AsyncSession = Depends(get_pg_session)):
    user = await UserService.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"} 