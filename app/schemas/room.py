from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
import datetime

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=255)
    is_private: Optional[bool] = False

class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=255)
    is_private: Optional[bool] = None

class RoomResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_private: bool
    created_by: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class RoomMembershipResponse(BaseModel):
    room_id: UUID
    user_id: UUID
    joined_at: datetime.datetime
    role: str
    is_active: bool 