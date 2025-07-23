from fastapi import APIRouter, Body, Depends
from app.core.database import redis
from app.tasks.celery_tasks import send_notification
from datetime import datetime

router = APIRouter()

@router.get("/{user_id}/presence")
async def get_user_presence(user_id: str):
    online = await redis.get(f"user:{user_id}:online")
    return {"online": bool(online)}

@router.post("/{user_id}/notify")
async def notify_user(user_id: str, message: str):
    send_notification.delay(user_id, message)
    return {"status": "notification task queued"}

@router.post("/{user_id}/report")
async def report_user(
    user_id: str,
    reason: str = Body(...),
    current_user = Depends(lambda: None),
    mongo_db=Depends(lambda: None)
):
    report = {
        "type": "user",
        "reported_user_id": user_id,
        "reporter_id": str(current_user.id),
        "reason": reason,
        "created_at": datetime.utcnow()
    }
    await mongo_db.reports.insert_one(report)
    return {"success": True} 