from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class Reaction(BaseModel):
    user_id: str
    emoji: str

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4096)
    message_type: str = Field("text")
    file_url: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Optional[Dict] = None

class MessageResponse(BaseModel):
    id: str
    room_id: str
    user_id: str
    username: str
    content: str
    message_type: str
    file_url: Optional[str]
    reply_to: Optional[str]
    reactions: List[Reaction] = []
    edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    metadata: Optional[Dict] = None 