import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.redis_client import redis_client
from unittest.mock import patch
import json

client = TestClient(app)

TEST_REPO_URL = "https://github.com/hwchase17/langchain"
TEST_PR_NUMBER = "32013"
TEST_NOT_FOUND_PR_NUMBER="322"

DUMMY_RESULT = {
    "summary": "Dummy summary",
    "review": "Dummy review",
    "length": 42,
    "repo_url": TEST_REPO_URL,
    "pr_number": TEST_PR_NUMBER
}


@pytest.fixture(autouse=True)
def clear_redis_before_each_test():
    redis_client.flushdb()


def test_analyze_pr_success():
    payload = {"repo_url": TEST_REPO_URL, "pr_number": TEST_PR_NUMBER}
    response = client.post("/analyze-pr", json=payload)
    assert response.status_code == 200
    assert "task_id" in response.json()


def test_analyze_pr_invalid_input():
    payload = {"repo_url": TEST_REPO_URL}
    response = client.post("/analyze-pr", json=payload)
    assert response.status_code == 422


def test_status_not_found():
    response = client.get(f"/status/{TEST_NOT_FOUND_PR_NUMBER}")
    assert response.status_code in (404, 422)

def test_task_results_success():
    from app.tasks import store_task_result
    store_task_result(TEST_PR_NUMBER, DUMMY_RESULT)
    response = client.get(f"/results/{TEST_PR_NUMBER}")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Dummy summary"
    assert data["pr_number"] == TEST_PR_NUMBER


def test_task_results_not_found():
    response = client.get("/task-results/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_cache_behavior():
    from app.tasks import store_task_result, get_cache_key
    KEY = get_cache_key(TEST_REPO_URL, TEST_PR_NUMBER)
    store_task_result(TEST_PR_NUMBER, DUMMY_RESULT,KEY)
    cached = redis_client.get(KEY)
    assert cached is not None
    cached_json = json.loads(cached)
    assert cached_json["review"] == "Dummy review"


@patch("app.tasks.fetch_pr_diff", return_value="diff --git a/foo.py b/foo.py")
@patch("app.tasks.summarize_and_review_diff", return_value=("summary", "review"))
def test_celery_task_runs(mock_review, mock_diff):
    from app.tasks import analyze_pr_task
    result = analyze_pr_task(TEST_REPO_URL, TEST_PR_NUMBER)
    assert result["summary"] == "summary"
    assert result["review"] == "review"
    assert result["repo_url"] == TEST_REPO_URL
