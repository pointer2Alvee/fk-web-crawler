from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
import hashlib

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from utilities.log_config import setup_logger


# Setup log config
log_config = setup_logger("db_logger")

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")

# Getting a Database named "scraped_books"
db = client.scraped_books

# **MongoDB schema / Getting a collection/table named "books"
collection_books = db["books"]
    
# Change Log collection/table
change_log = db["change_log"]



# Helper Func : ** Fingerprint Hash generator
def compute_fingerprint(doc: dict) -> str:
    """
    Computes a fingerprint hash from the possible changing fields.
    """
    key_fields = [
        doc.get("name", ""),
        doc.get("price_with_tax", ""),
        doc.get("price_without_tax", ""),
        doc.get("availability", ""),
        doc.get("rating", ""),
    ]
    
    combined = "|".join(key_fields)
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


# Insert Data (books) to MongoDB
def insert_to_db(book_name, book_description, book_category,book_price_with_tax, book_price_without_tax, book_availability, book_review, book_cover_image_url, book_rating, crawl_timestamp, source_url, status, raw_html): 
    """
    This method inserts or updates each scraped book data to mongoDB Atlas, and log any changes to a separate collection.
    """
    # Insert Document // The newly scraped data
    doc = {
            "name": book_name,
            "description": book_description,
            "category": book_category,
            "price_with_tax": book_price_with_tax,
            "price_without_tax": book_price_without_tax,
            "availability": book_availability,
            "review": book_review,
            "cover_image_url": book_cover_image_url,
            "rating": book_rating,
            
            # ** For storing metadata
            "crawl_timestamp":crawl_timestamp,
            "source_url": source_url,
            "status": status, 
            
            # ** raw HTML snapshot
            "raw_html" : raw_html,
    }
    
    # Compute content fingerprint
    doc["fingerprint"] = compute_fingerprint(doc)   

    
    # Working State for insertion to db
    # inserted_book = collection_books.insert_one(doc)
    # return inserted_book.inserted_id

    if not source_url:
        print("Skipping insert: source_url is missing.")
        return None
    
    # ** resuming from the last successful crawl with upsert + source_url check
    # ** data insertion with deduplication feature
    # ** Finding existing records and change detection + change logging 
    try:         
        # Finding existing records - ** deduplication works here
        existing = collection_books.find_one({"source_url": source_url}) 
        
        if existing:
            # ** Change Detection : compare and track all field [name,price etc] changes - without fingerprinting strategy 
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
                    
            # ** Change Detection : compare and track changes only fingerprint changes- with fingerprinting strategy 
            old_fingerprint = existing.get("fingerprint")
            new_fingerprint = doc["fingerprint"]
            
            # ** First, checks if fingerprint-field changed
            if old_fingerprint != new_fingerprint: #  key != "crawl_timestamp" ==> not needed as fingerprint is not compute based on crawl_timestamp 
                
                
                # ** Second, Track Changes of other fields
                changes = {}
                for key, new_val in doc.items():
                    old_val = existing.get(key) # Retrives value/col like "book_name" of current 'key' from db
                    
                    if old_val != new_val: #  key != "crawl_timestamp" not needed
                        changes[key] = {
                            "old" : old_val,
                            "new" : new_val, 
                        }
                        
                # ** log config - for changes
                log_config.info(f"[ALERT!] changes detected for book:-  '{book_name}' ")
                
                # Update the document        
                collection_books.update_one({"_id": existing["_id"]}, {"$set": doc})
                
                # ** If changes found, update doc and log them 
                change_log.insert_one({
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
                change_log.insert_one({
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
         
        else:
            # insert new book + log Changes   
            inserted = collection_books.insert_one(doc)
            change_log.insert_one({
                "source_url": source_url,
                "name": book_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "changes": "New book inserted"
            })
            print(f"New book Scraped and inserted + logged: {source_url}")
            
            # ** log config - for new book
            log_config.info(f"[ALERT!] New added book:-  '{book_name}'  ")
                
            return inserted.inserted_id
                
    except DuplicateKeyError:
        print(f"[Duplicate] Skipping: {source_url}")
        return  None
    except Exception as e:
        print(f"[MongoDB Error] {e}")
        return  None 