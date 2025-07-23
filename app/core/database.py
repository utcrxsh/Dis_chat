import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import aioredis
from .config import settings

# PostgreSQL (SQLAlchemy async)
DATABASE_URL = settings.postgresql_url
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_pg_session():
    async with AsyncSessionLocal() as session:
        yield session

async def pg_health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False

# MongoDB (Motor)
mongo_client: AsyncIOMotorClient = None
def get_mongo_client():
    return mongo_client

async def mongo_connect():
    global mongo_client
    mongo_client = AsyncIOMotorClient(settings.mongodb_url)

def get_mongo_db():
    return mongo_client[settings.mongodb_name]

async def mongo_health_check():
    try:
        await mongo_client.admin.command('ping')
        return True
    except Exception:
        return False

# Redis (aioredis)
redis = None
async def redis_connect():
    global redis
    redis = await aioredis.from_url(settings.redis_url, decode_responses=True)

async def redis_health_check():
    try:
        pong = await redis.ping()
        return pong
    except Exception:
        return False

async def connect():
    await mongo_connect()
    await redis_connect()

async def disconnect():
    if mongo_client:
        mongo_client.close()
    if redis:
        await redis.close() 