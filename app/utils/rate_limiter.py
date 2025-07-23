from functools import wraps
import time
from typing import Dict, Callable, Optional
from fastapi import Request, HTTPException, status, Depends
from app.core.config import settings
from app.core.database import redis

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, key: str) -> bool:
        now = int(time.time())
        window_start = now - self.window_seconds
        # Use Redis sorted set for sliding window
        key_name = f"rate:{key}"
        await redis.zremrangebyscore(key_name, 0, window_start)
        count = await redis.zcard(key_name)
        if count >= self.max_requests:
            return False
        await redis.zadd(key_name, {str(now): now})
        await redis.expire(key_name, self.window_seconds)
        return True

rate_limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window)

def rate_limit(max_requests: int = None, window_seconds: int = None):
    max_requests = max_requests or settings.rate_limit_requests
    window_seconds = window_seconds or settings.rate_limit_window
    limiter = RateLimiter(max_requests, window_seconds)
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            user = kwargs.get('current_user', None)
            key = str(user.id) if user else request.client.host
            allowed = await limiter.is_allowed(key)
            if not allowed:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
            return await func(*args, **kwargs)
        return wrapper
    return decorator 