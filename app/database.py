# app/database.py
from redis import Redis
from app.config import settings
import json

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def store_task_result(pr_number, result, cache_key=None):
    redis_client.set(f"task:{pr_number}:result", json.dumps(result))

    if cache_key:
        redis_client.setex(cache_key, 60 * 60 * 24, json.dumps(result))

def store_task_status(pr_number):
    redis_client.set(f"task:{pr_number}:status", "completed")

def store_task_error(pr_number, error):
    redis_client.set(f"task:{pr_number}:status", "failed")
    redis_client.set(f"task:{pr_number}:error", error)

def get_task_status(pr_number):
    return redis_client.get(f"task:{pr_number}:status")

def get_task_result(pr_number):
    result = redis_client.get(f"task:{pr_number}:result")
    return json.loads(result) if result else {"status": "not_found"}
