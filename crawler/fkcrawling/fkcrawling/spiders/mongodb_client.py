import sys
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from utilities.log_config import setup_logger

from dotenv import load_dotenv
load_dotenv()

# Connect to MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")  # Access 'MONGODB_URI' from .env
client = MongoClient(MONGODB_URI)       # Making a Connection with MongoClient

# Create database "scraped_books"
db = client.scraped_books

# Get collection/table "books" & "change_log" / ** --> MongoDB schema 
collection_books = db["books"]
collection_change_log = db["change_log"]

# Setup log-config
log_config = setup_logger("db_logger")

# ** --> Fingerprint-strategy : Hash generator
def compute_fingerprint(doc: dict) -> str:
    """
    Computes a fingerprint hash from the possible frequently changing fields.
    
    Params :
        doc (dict) : document with fields that is used to generate fingerprint
        
    Returns:
        md5 coded Fingerprint hash 
    """
    
    # Frequent Chaning Fields
    key_fields = [
        doc.get("name", ""),
        doc.get("price_with_tax", ""),
        doc.get("price_without_tax", ""),
        doc.get("availability", ""),
        doc.get("rating", ""),
    ]
    
    # Converts to string and combines all these fields 
    combined = "|".join(map(str, key_fields))
    
    # Generate & returns hash from 'combined' string 
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


# Inserts book data to MongoDB
def insert_to_db(book_name, book_description, book_category,book_price_with_tax, book_price_without_tax, book_availability, book_review, book_cover_image_url, book_rating, crawl_timestamp, source_url, status, raw_html): 
    """
    This method inserts newly scraped book data or updates existing ones to mongoDB Atlas, and log any changes to a separate collection.
    """
    # New book Document
    doc = {
            # Individual book's scraped data
            "name": book_name,
            "description": book_description,
            "category": book_category,
            "price_with_tax": book_price_with_tax,
            "price_without_tax": book_price_without_tax,
            "availability": book_availability,
            "review": book_review,
            "cover_image_url": book_cover_image_url,
            "rating": book_rating,
            
            # ** --> metadata
            "crawl_timestamp":crawl_timestamp,
            "source_url": source_url,
            "status": status, 
            
            # ** --> raw HTML snapshot
            "raw_html" : raw_html,
    }
    
    # Compute doc's fingerprint and insert it as a new "key:val" pair
    doc["fingerprint"] = compute_fingerprint(doc)   

    # Working State for insertion to db
    # inserted_book = collection_books.insert_one(doc)
    # return inserted_book.inserted_id

    if not source_url:
        print("Skipping insert: source_url is missing.")
        return None
    
    # ** --> Resume from last successful crawl with source_url check, data insert & update with deduplication check, find existing records and change detection + change logging 
    try:         
        # Finding existing records / ** --> deduplication works here
        existing = collection_books.find_one({"source_url": source_url}) 
        
        # If Existing, then update Document
        if existing:
            # ** Change Detection : compare and track all field [name,price etc] changes - without fingerprinting strategy - NOT USED
            """
            changes = {}
            for key, new_val in doc.items():
                old_val = existing.get(key) # Retrives value/col like "book_name" of current 'key' from db
                
                if key != "crawl_timestamp" and old_val != new_val: #  key != "crawl_timestamp" ==> avoids checking crawling_time as it will be diff every time and log it unnecessarily
                    changes[key] = {
                        "old" : old_val,
                        "new" : new_val, 
                    }
            """
                    
            # ** --> Change Detection : compare and track changes only fingerprint changes - with fingerprinting strategy 
            old_fingerprint = existing.get("fingerprint")
            new_fingerprint = doc["fingerprint"]
            
            # ** --> Firstly, checks if fingerprint-field changed
            if old_fingerprint != new_fingerprint: #  key != "crawl_timestamp" ==> not needed as fingerprint is not compute based on crawl_timestamp 
                    
                # ** --> Secondly, track Changes of other fields
                changes = {}
                for key, new_val in doc.items():
                    old_val = existing.get(key) # Retrives value/col like "book_name" of current 'key' from db
                    
                    if old_val != new_val: #  key != "crawl_timestamp" not needed
                        changes[key] = {
                            "old" : old_val,
                            "new" : new_val, 
                        }
                        
                # ** --> Registers major Changes as ALERT in log file 
                log_config.info(f"[ALERT!] changes detected for book:-  '{book_name}' ")
                
                # Update the document        
                collection_books.update_one({"_id": existing["_id"]}, {"$set": doc})
                
                # ** --> If changes found, update doc and log them in DB
                collection_change_log.insert_one({
                    "source_url": source_url,
                    "name": book_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "changes": {
                        "fingerprint_changed": True,
                        "field_changes": changes 
                    }
                })
                print(f"Fingerprint/Hash changes detected & logged for: {source_url}")
            else:
                print(f"No change detected (fingerprint same) for: {source_url}")
            return "updated"
            
            """
            # If changes found, update doc and log them 
            if changes:
                collection_books.update_one({"_id":existing["_id"]}, {"$set" : doc})
                collection_change_log.insert_one({
                    "source_url": source_url,
                    "name": book_name,
                    "timestamp":  datetime.now(timezone.utc).isoformat(),
                    "changes": changes
                })
                print(f"Changes detected & logged for: {source_url}")
            else:
                print(f"No changes for: {source_url}")
            return "updated
            """
            
        # If New, then insert new book Document
        else:
            # insert new book + log Changes   
            inserted = collection_books.insert_one(doc)
            collection_change_log.insert_one({
                "source_url": source_url,
                "name": book_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "changes": "New book inserted"
            })
            print(f"New book Scraped and inserted + logged: {source_url}")
            
            # ** --> Registers new book as ALERT in log file 
            log_config.info(f"[ALERT!] New added book:-  '{book_name}'  ")
                
            return inserted.inserted_id
                
    except DuplicateKeyError:
        print(f"[Duplicate] Skipping: {source_url}")
        return  None
    
    except Exception as e:
        print(f"[MongoDB Error] {e}")
        return  None 