from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database URLs
    postgresql_url: str = "postgresql+asyncpg://user:password@localhost/chatdb"
    mongodb_url: str = "mongodb://localhost:27017"
    redis_url: str = "redis://localhost:6379"
    
    # JWT Settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # MongoDB Database
    mongodb_name: str = "chat_db"
    
    # Redis Settings
    redis_expire_seconds: int = 3600
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings() 