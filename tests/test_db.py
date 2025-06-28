from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

def test_mongo_connection():
    client = MongoClient(MONGODB_URI)
    db = client.get_database("scraped_books")
    assert db is not None
    assert "books" in db.list_collection_names() or "change_log" in db.list_collection_names()
