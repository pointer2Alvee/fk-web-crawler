from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    book_name: str
    book_description: Optional[str]
    book_category: str
    book_price_with_tax: float
    book_price_without_tax: float
    book_availability: Optional[str]
    book_review: Optional[int]
    book_cover_image_url: str # if : Optional[HttpUrl] -> doesnt upload to DB
    book_rating: int 
    crawl_timestamp: datetime
    source_url: str # if : Optional[HttpUrl] -> doesnt upload to DB
    status: str
    raw_html: Optional[str] = Field(default=None) 
