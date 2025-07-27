# app/tasks.py
import json
import hashlib
from loguru import logger
from app.celery_worker import celery_app
from app.github_utils import fetch_pr_diff
from app.database import store_task_result, store_task_error,store_task_status
from app.llm_utils import summarize_and_review_diff
from app.redis_client import redis_client

def get_cache_key(repo_url: str, pr_number: int):
    raw = f"{repo_url}:{pr_number}"
    return "analyze_pr:" + hashlib.sha256(raw.encode()).hexdigest()

@celery_app.task(name="app.tasks.analyze_pr_task")
def analyze_pr_task(repo_url, pr_number, github_token=None):
    logger.info(f"Task {analyze_pr_task.request.id}: Starting analysis")
    cache_key = get_cache_key(repo_url, pr_number)

    cached = redis_client.get(cache_key)
    if cached:
        logger.info("Cache hit")
        store_task_status(pr_number)
        return json.loads(cached)

    logger.info("Cache miss")
    try:
        diff = fetch_pr_diff(repo_url, pr_number, github_token)
        logger.info(f"Task {analyze_pr_task.request.id}: Fetched diff (len={len(diff)})")

        summary, review = summarize_and_review_diff(diff)

        result = {
            "summary": summary,
            "review": review,
            "length": len(diff),
            "repo_url": repo_url,
            "pr_number": pr_number
        }

        store_task_result(pr_number, result,cache_key)
        store_task_status(pr_number)
        logger.info(result)
        return result

    except Exception as e:
        logger.exception("Task failed")
        store_task_error(pr_number,e)
        logger.error(f"Task {pr_number}: Failed with error {e}")
        raise e
