from celery import Celery
from app.core.config import settings
from celery.schedules import crontab

celery_app = Celery(
    "job_matcher",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.parse_jobs"]
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "parse-jobs-every-hour": {
        "task": "app.tasks.parse_jobs.parse_jobs",
        "schedule": crontab(minute=0, hour="*"),
    }
}

celery_app.autodiscover_tasks(["app.tasks"])