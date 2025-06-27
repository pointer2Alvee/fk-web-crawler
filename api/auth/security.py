from fastapi import Header, HTTPException
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
load_dotenv()

# Access variables
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

limiter = Limiter(key_func=get_remote_address)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
