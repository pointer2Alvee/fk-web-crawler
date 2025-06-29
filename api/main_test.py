# -- THIS FILE ONLY FOR TESTING ---
from fastapi import FastAPI, APIRouter,  HTTPException
from pymongo.mongo_client import MongoClient
from models.book import Book
import os
from bson.objectid import ObjectId
test_app = FastAPI()
test_router = APIRouter()


# Access variables
MONGODB_URI = os.getenv("MONGODB_URI")

# basic mongoDB connection with api app "test_app"
client = MongoClient(MONGODB_URI)

# Getting a Database named "scraped_books"
db = client.scraped_books

# **MongoDB schema / Getting a collection/table named "books"
collection = db["books"]

# **MongoDB schema / Getting a collection/table named "change_log"
my_change_log = db["change_log"]

# basic get() and shows in swagger UI
@test_app.get("/")
async def show_msg():
    return {
            "id" : 1,
            "message": "Hello"
            }

@test_app.get("/")
async def home():
    return {"message": "Hello World"}


# Helper function to convert MongoDB document to a serializable dictionary
def serialize_book(book):
    return {
        "id": str(book["_id"]),
        "name": book.get("name"),
        "description": book.get("description"),
        "category": book.get("category"),
        "price_with_tax": book.get("price_with_tax"),
        "price_without_tax": book.get("price_without_tax"),
        "availability": book.get("availability"),
        "review": book.get("review"),
        "cover_image_url": book.get("cover_image_url"),
        "rating": book.get("rating"),
        "crawl_timestamp": book.get("crawl_timestamp"),
        "source_url": book.get("source_url"),
        "status": book.get("status"),
        "raw_html": book.get("raw_html"),
        "fingerprint": book.get("fingerprint")
    }

def serialzie_change_log(log):
    if not log:
        return {"error": "No data found"}
    return {
        "id": str(log["_id"]),
        "name": log.get("name"),
        "crawl_timestamp": log.get("timestamp"),
        "source_url": log.get("source_url"),
        "changes" : log.get("changes")
    }
    
# basic get() retreiving data from mongodb and shows in swagger UI
@test_router.get("/books")
async def get_all_books():
    books = collection.find()
    return [serialize_book(book) for book in books]

# basic get() retreiving individual data from mongodb and shows in swagger UI
@test_router.get("/books/{book_id}")
async def get_book(book_id:str):
    book_id = ObjectId(book_id)
    book = collection.find_one({"_id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Change log not found")
    return serialize_book(book)


# basic get() retreiving data from mongodb and shows in swagger UI
@test_router.get("/change_log")
async def get_all_change_log():
    logs = my_change_log.find()
    return [serialzie_change_log(log) for log in logs]

# basic get() retreiving individual data from mongodb and shows in swagger UI
@test_router.get("/change_log/{log_id}")
async def get_change_log(log_id:str):
    log_id = ObjectId(log_id)
    log = my_change_log.find_one({"_id": log_id})
    if not log:
        raise HTTPException(status_code=404, detail="Change log not found")
    return serialzie_change_log(log)


# including routers to fast api app 
test_app.include_router(test_router)