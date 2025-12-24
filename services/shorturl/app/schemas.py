from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ShortenRequest(BaseModel):
    url: str = Field(..., description='Full URL to shorten')

    @field_validator('url', mode='before')
    def validate_url(cls, v):  # noqa
        print(v)
        parsed = urlparse(v)
        print(parsed)

        if not parsed.scheme:
            raise ValueError('URL must have a scheme (http:// or https://)')

        if parsed.scheme not in ('http', 'https'):
            raise ValueError('URL scheme must be http or https')

        if not parsed.netloc:
            raise ValueError('URL must have a host/domain')

        if not parsed.netloc.strip():
            raise ValueError('URL host cannot be empty')

        return v.strip()


class ShortenResponse(BaseModel):
    short_id: str
    short_url: str
    full_url: str


class ShortUrlStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_id: str
    full_url: str
    created_at: datetime
