from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")

# Getting a Database named "scraped_books"
db = client.scraped_books

# **MongoDB schema / Getting a collection/table named "books"
collection = db["books"]
    

# Insert Data (books) to MongoDB
def insert_to_db(book_name, book_description, book_category,book_price_with_tax, book_price_without_tax, book_availability, book_review, book_cover_image_url, book_rating, crawl_timestamp, source_url, status, raw_html): 
    """
    This method inserts each scraped book data to mongoDB Atlas
    """
    # Insert Document 
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
    # inserted_book = collection.insert_one(doc)
    # return inserted_book.inserted_id

    if not source_url:
        print("Skipping insert: source_url is missing.")
        return None
    
    # ** resuming from the last successful crawl with upsert + source_url check
    # ** data insertion with deduplication feature
    try:
        result = collection.update_one(
            {"source_url": source_url},  # Unique key / deduplication based on URL
            {"$set": doc},
            upsert=True
        )
        return  result.upserted_id or "updated"
    except DuplicateKeyError:
        print(f"[Duplicate] Skipping: {source_url}")
        return  None
    except Exception as e:
        print(f"[MongoDB Error] {e}")
        return  None 