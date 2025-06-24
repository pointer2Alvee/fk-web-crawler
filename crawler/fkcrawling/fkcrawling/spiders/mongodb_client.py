from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")

# Getting a Database named "scraped_books"
db = client.scraped_books

# **MongoDB schema / Getting a collection/table named "books"
collection_books = db["books"]
    
# Change Log collection/table
change_log = db["change_log"]

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
            "crawl_timestamp":crawl_timestamp,
            "source_url": source_url,
            "status": status, 
            "raw_html" : raw_html,
    }
    
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
            # compare and track changes
            changes = {}
            for key, new_val in doc.items():
                old_val = existing.get(key) # Retrives value/col like "book_name" of current 'key' from db
                
                if key != "crawl_timestamp" and old_val != new_val: #  key != "crawl_timestamp" ==> avoids checking crawling_time as it will be diff every time and log it unnecessarily
                    changes[key] = {
                        "old" : old_val,
                        "new" : new_val, 
                    }
            
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
            return "updated"
         
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
            return inserted.inserted_id
                
    except DuplicateKeyError:
        print(f"[Duplicate] Skipping: {source_url}")
        return  None
    except Exception as e:
        print(f"[MongoDB Error] {e}")
        return  None 