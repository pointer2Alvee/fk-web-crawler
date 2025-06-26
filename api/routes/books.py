from fastapi import APIRouter, Query, Depends, HTTPException
from pymongo import MongoClient
from typing import List, Optional
from models.book import Book
from auth.security import verify_api_key
from models.schemas import convert_all_books, convert_individual_book
from fastapi_pagination import Page, paginate
from bson.objectid import ObjectId

router = APIRouter()

# Making a Connection with MongoClient
client = MongoClient("mongodb+srv://fkcrawler_Alvee:fk1234@fkwebcrawler.ozzbwx0.mongodb.net/")

# Getting a Database named "scraped_books"
db = client.scraped_books

# **MongoDB schema / Getting a collection/table named "books"
collection_books = db["books"]

# ** get all books
@router.get("/books")
async def get_books(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    rating: Optional[str] = None,
    sort_by: Optional[str] = Query(None, enum=["rating", "price_with_tax", "review"]),
    api_key: str = Depends(verify_api_key)
):
    query = {}
    if category:
        query["category"] = category
    if rating:
        query["rating"] = rating
    if min_price or max_price:
        query["price_with_tax"] = {}
        if min_price:
            query["price_with_tax"]["$gte"] = min_price
        if max_price:
            query["price_with_tax"]["$lte"] = max_price

    books = list(collection_books.find(query))
    if sort_by:
        books = sorted(books, key=lambda x: x.get(sort_by, 0), reverse=True)

    results = []
    for b in books:
        b["book_name"] = b.get("name")
        b["book_description"] = b.get("description")
        b["book_category"] = b.get("category")
        b["book_price_with_tax"] = b.get("price_with_tax")
        b["book_price_without_tax"] = b.get("price_without_tax")
        b["book_availability"] = b.get("availability")
        b["book_review"] = b.get("review")
        b["book_cover_image_url"] = b.get("cover_image_url")
        b["book_rating"] = b.get("rating")
        b["crawl_timestamp"] = b.get("crawl_timestamp")
        b["source_url"] = b.get("source_url")
        
        # Auto-validation with pydantic 
        book = Book(**b)
        
        # getting only 3 fields in swagger UI while all fields gets validated
        results.append(book.model_dump(include={"book_name", "book_category", "book_price_with_tax"})) 


    return results

    # manual serialization
    # return convert_all_books(books)
    # # return paginate(books)


@router.get("/books/{book_id}", response_model=Book)
def get_book_by_id(book_id: str):
    book_id = ObjectId(book_id)
    book = collection_books.find_one({"_id": book_id})
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Rename DB keys to match Pydantic model fields
    book["book_name"] = book.get("name")
    book["book_description"] = book.get("description")
    book["book_category"] = book.get("category")
    book["book_price_with_tax"] = book.get("price_with_tax")
    book["book_price_without_tax"] = book.get("price_without_tax")
    book["book_availability"] = book.get("availability")
    book["book_review"] = book.get("review")
    book["book_cover_image_url"] = book.get("cover_image_url")
    book["book_rating"] = book.get("rating")
    book["crawl_timestamp"] = book.get("crawl_timestamp")
    book["source_url"] = book.get("source_url")

    # Validate through Pydantic
    return Book(**book)
    
    # manual serialization
    # return convert_individual_book(book)
