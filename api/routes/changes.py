from fastapi import APIRouter, Depends, HTTPException
from auth.security import verify_api_key
from pymongo import MongoClient
from models.change import Change

from bson.objectid import ObjectId
from models.schemas import convert_all_change_logs

router = APIRouter()

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")

# Getting a Database named "scraped_books"
db = client.scraped_books 

# **MongoDB schema / Getting a collection/table named "change_log"
change_log = db["change_log"]

@router.get("/changes")
async def get_change_log():
    changes = list(change_log.find().sort("timestamp", -1).limit(10)) # sort reversly, show last 10 logs
    if not changes:
        raise HTTPException(status_code=404, detail="Change log not found")
    
    # ** with pydantic
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
    
    # ** without pydantic
    return convert_all_change_logs(changes)


