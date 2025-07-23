from celery import Celery
import os

celery_app = Celery(
    "chat_app",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

celery_app.conf.beat_schedule = {
    'cleanup-old-messages-daily': {
        'task': 'app.tasks.celery_tasks.cleanup_old_messages',
        'schedule': 60 * 60 * 24,  # every 24 hours
    },
    'generate-analytics-hourly': {
        'task': 'app.tasks.celery_tasks.generate_analytics',
        'schedule': 60 * 60,  # every hour
    },
}

@celery_app.task
def send_notification(user_id: str, message: str):
    print(f"Send notification to {user_id}: {message}")
    return True

@celery_app.task
def cleanup_old_messages():
    print("Cleanup old messages task running...")
    return True

@celery_app.task
def generate_analytics():
    print("Generate analytics task running...")
    return True 