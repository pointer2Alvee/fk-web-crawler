from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class Change(BaseModel):
    log_name: Optional[str]
    log_timestamp: Optional[datetime]
    source_url: Optional[str] #Optional[HttpUrl] 
    # log_changes : Optional[str] # NOT WORKING
