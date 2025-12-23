from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase


class AbstractModel(DeclarativeBase):
    pass


class TodoItem(AbstractModel):
    __tablename__ = 'todo_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

