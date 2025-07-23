from fastapi import FastAPI
from app.core import database
from contextlib import asynccontextmanager
from app.api import auth, rooms, messages
from fastapi.staticfiles import StaticFiles
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(title="Distributed Chat API", lifespan=lifespan)

# Serve uploaded files
UPLOAD_DIR = os.path.abspath("uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

@app.get("/health")
async def health():
    pg = await database.pg_health_check()
    mongo = await database.mongo_health_check()
    redis = await database.redis_health_check()
    return {"postgres": pg, "mongodb": mongo, "redis": redis} 