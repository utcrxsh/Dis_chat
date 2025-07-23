from typing import Optional, List, Dict
from datetime import datetime

class Message:
    def __init__(
        self,
        room_id: str,
        user_id: str,
        username: str,
        content: str,
        message_type: str = "text",
        file_url: Optional[str] = None,
        reply_to: Optional[str] = None,
        reactions: Optional[List[Dict]] = None,
        edited: bool = False,
        edited_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[dict] = None,
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.room_id = room_id
        self.user_id = user_id
        self.username = username
        self.content = content
        self.message_type = message_type
        self.file_url = file_url
        self.reply_to = reply_to
        self.reactions = reactions or []
        self.edited = edited
        self.edited_at = edited_at
        self.created_at = created_at or datetime.utcnow()
        self.metadata = metadata or {} 