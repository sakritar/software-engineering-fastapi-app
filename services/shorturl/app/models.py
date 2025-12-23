from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase


class AbstractModel(DeclarativeBase):
    pass


class ShortUrl(AbstractModel):
    __tablename__ = 'short_urls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_id = Column(String(20), unique=True, nullable=False, index=True)
    full_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

