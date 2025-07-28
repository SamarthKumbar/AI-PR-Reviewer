# rate_limit.py

from fastapi import Request, HTTPException
from app.redis_client import redis_client  

RATE_LIMIT = 10       
WINDOW_SECONDS = 60      

def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    return request.client.host

def is_rate_limited(ip: str) -> bool:
    key = f"rate_limit:{ip}"
    current_count = redis_client.get(key)

    if current_count is None:
        redis_client.set(key, 1, ex=WINDOW_SECONDS)
        return False
    elif int(current_count) < RATE_LIMIT:
        
        redis_client.incr(key)
        return False
    else:
        
        return True
