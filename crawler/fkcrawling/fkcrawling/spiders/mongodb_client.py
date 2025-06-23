from pymongo import MongoClient
import datetime

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")

# Getting a Database named "scraped_books"
db = client.scraped_books

# Getting a collection/table named "books"
collection = db["books"]
    

# Insert Data (books) to MongoDB
def insert_to_db(book_name, book_description, book_category,book_price_with_tax, book_price_without_tax, book_availability, book_review, book_cover_image_url, book_rating, crawl_timestamp, source_url, status): 
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
    }
    
    inserted_book = collection.insert_one(doc)
    return inserted_book.inserted_id