"""Celery uses Redis for delivery. PostgreSQL owns durable job and clinical state."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "medilink", broker=settings.celery_broker_url, include=["app.workers.tasks.maintenance"]
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_ignore_result=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    broker_transport_options={"visibility_timeout": 600},
    task_soft_time_limit=240,
    task_time_limit=300,
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "durable-jobs": {"task": "medilink.drain_jobs", "schedule": 10.0},
        "medication-reminders": {"task": "medilink.medication_tick", "schedule": 60.0},
    },
)
