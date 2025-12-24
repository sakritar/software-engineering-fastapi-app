from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime


class ShortenRequest(BaseModel):
    url: str = Field(..., description="Full URL to shorten")


class ShortenResponse(BaseModel):
    short_id: str
    short_url: str


class ShortUrlStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    short_id: str
    full_url: str
    created_at: datetime
