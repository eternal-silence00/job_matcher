from celery import Celery
from app.core.config import settings
from celery.schedules import crontab

celery_app = Celery(
    "job_matcher",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.parse_jobs", "app.tasks.notify_users", "app.tasks.cleanup_jobs"]
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "parse-jobs-every-hour": {
        "task": "app.tasks.parse_jobs.parse_jobs",
        "schedule": crontab(minute=0, hour="*"),
    },
    "notify-users-daily": {
    "task": "app.tasks.notify_users.notify_users",
    "schedule": crontab(minute=0, hour=9),
    },
    "cleanup_old_jobs": {
    "task": "app.tasks.cleanup_jobs.cleanup_old_jobs",
    "schedule": crontab(minute=0, hour=3),
    }
}
