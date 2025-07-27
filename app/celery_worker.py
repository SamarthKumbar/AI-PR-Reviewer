# app/celery_worker.py
from celery import Celery
from app.config import settings  

celery_app = Celery(
    'worker',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)


celery_app.autodiscover_tasks(['app'])


import app.tasks  
