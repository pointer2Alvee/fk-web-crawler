from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    book_name: str
    book_description: Optional[str]
    book_category: str
    book_price_with_tax: str
    book_price_without_tax: str
    book_availability: Optional[str]
    book_review: Optional[str]
    book_cover_image_url: str # if : Optional[HttpUrl] -> doesnt upload to DB
    book_rating: Optional[str]
    crawl_timestamp: datetime
    source_url: str # if : Optional[HttpUrl] -> doesnt upload to DB
    status: str
    raw_html: Optional[str] = Field(default=None)
