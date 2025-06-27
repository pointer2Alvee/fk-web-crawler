from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class Book(BaseModel): # BaseModel- Defines data models with automatic validation and parsing.
    """
    A Pydantic model for validating and documenting the structure of the book data scraped, before storing it into MongoDB.
    Any instance of this class will automatically validate and convert data passed to it.
    """
    book_name: str
    book_description: Optional[str]  # Optional Indicates a field is not required (i.e., it can be None)
    book_category: str
    book_price_with_tax: float
    book_price_without_tax: float
    book_availability: Optional[str]
    book_review: Optional[int]
    book_cover_image_url: str # ** problem if : Optional[HttpUrl] -> doesnt upload to DB
    book_rating: int 
    
    # Metadata
    crawl_timestamp: datetime
    source_url: str # ** problem if : Optional[HttpUrl] -> doesnt upload to DB
    status: str
    raw_html: Optional[str] = Field(default=None) 
