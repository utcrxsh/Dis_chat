import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    is_private = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    memberships = relationship("RoomMembership", back_populates="room")

class RoomMembership(Base):
    __tablename__ = "room_memberships"

    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    role = Column(String(16), default="member")  # admin, member
    is_active = Column(Boolean, default=True)

    room = relationship("Room", back_populates="memberships") 