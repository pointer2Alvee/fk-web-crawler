from fastapi import Header, HTTPException
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

API_KEY = os.getenv("API_KEY", "123456")

limiter = Limiter(key_func=get_remote_address)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
