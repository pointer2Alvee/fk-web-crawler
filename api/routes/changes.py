import os
from fastapi import APIRouter, Depends, HTTPException
from auth.security import verify_api_key
from pymongo import MongoClient
from models.change import Change # - NOT USED

from bson.objectid import ObjectId
from models.schemas import convert_all_change_logs
from fastapi import Request  
from utils.rate_limiter import limiter

from dotenv import load_dotenv
load_dotenv()

# Create APi Router
router = APIRouter()

# Connect to MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")  # Access 'MONGODB_URI' from .env
client = MongoClient(MONGODB_URI)       # Making a Connection with MongoClient

# Get a Database named "scraped_books"
db = client.scraped_books 

# Get a collection/table named "change_log"
change_log = db["change_log"]

@limiter.limit("100/hour") # Rate limiter
@router.get("/changes")

async def get_change_log( request : Request, api_key: str = Depends(verify_api_key)):
    changes = list(change_log.find().sort("timestamp", -1).limit(10)) # sort reversly, show last 10 logs
    if not changes:
        raise HTTPException(status_code=404, detail="Change log not found")
    
    # ** with pydantic - Gives error  - NOT USED
    # results = []
    # for c in changes:
    #     c["log_name"] = c.get("name")
    #     c["log_timestamp"] = c.get("timestamp")
    #     c["source_url"] = c.get("source_url")
    #     c["log_changes"] = c.get("changes")
        
    #     # Auto-validation with pydantic 
    #     change = Change(**c)
        
    #     # getting only 3 fields in swagger UI while all fields gets validated
    #     results.append(change.model_dump(include={"log_name", "log_timestamp", "log_changes"})) 

    # Validate through Pydantic
    # return results
    
    # ** without pydantic - with serialization
    return convert_all_change_logs(changes)


