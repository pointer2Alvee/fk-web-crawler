from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    book_name: Optional[str]
    book_description: Optional[str]
    book_category: Optional[str]
    book_price_with_tax: Optional[str]
    book_price_without_tax: Optional[str]
    book_availability: Optional[str]
    book_review: Optional[str]
    book_cover_image_url: Optional[str] #Optional[HttpUrl] 
    book_rating: Optional[str]
    crawl_timestamp: Optional[datetime]
    source_url: Optional[str] #Optional[HttpUrl] 
