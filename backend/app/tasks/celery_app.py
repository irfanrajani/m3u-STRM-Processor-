"""Celery application configuration."""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "iptv_manager",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.sync_tasks",
        "app.tasks.health_tasks",
        "app.tasks.vod_tasks",
        "app.tasks.epg_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "health-check-daily": {
        "task": "app.tasks.health_tasks.run_health_check",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    "epg-refresh-daily": {
        "task": "app.tasks.epg_tasks.refresh_all_epg",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "sync-providers-hourly": {
        "task": "app.tasks.sync_tasks.sync_all_providers",
        "schedule": crontab(minute=0),  # Every hour
    },
}
