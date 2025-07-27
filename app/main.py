# app/main.py
from fastapi import FastAPI,HTTPException,Request
from app.tasks import analyze_pr_task
from pydantic import BaseModel
from app.database import get_task_status, get_task_result
from app.rate_limit import get_client_ip,is_rate_limited

app = FastAPI()

class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None

@app.post("/analyze-pr")
def analyze_pr(request: AnalyzePRRequest,req: Request):
    ip = get_client_ip(req)
    if is_rate_limited(ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in 60 seconds.")
    
    task = analyze_pr_task.delay(request.repo_url, request.pr_number, request.github_token)
    return {"task_id": task.id}

@app.get("/status/{pr_number}")
def get_status(pr_number: str):
    status = get_task_status(pr_number)
    if status:
        return {"task_id": pr_number, "status": status}
    else:
        raise HTTPException(status_code=404, detail="Not Found")
    

@app.get("/results/{pr_number}")
def get_results(pr_number: str):
    result = get_task_result(pr_number)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Not Found")
