# app/github_utils.py
import requests
from loguru import logger

def fetch_pr_diff(repo_url: str, pr_number: int, github_token: str = None):

    logger.info(f"Fetching diff for PR #{pr_number} from {repo_url}")

    owner_repo = repo_url.replace("https://github.com/", "").strip("/")
    headers = {
        "Accept": "application/vnd.github.v3.diff"
    }

    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    diff_url = f"https://api.github.com/repos/{owner_repo}/pulls/{pr_number}"

    response = requests.get(diff_url, headers=headers, allow_redirects=True)

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

    return response.text
