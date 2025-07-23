from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 