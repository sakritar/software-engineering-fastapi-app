import os
from contextlib import asynccontextmanager
from typing import Generator

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import AbstractModel

database_url = os.getenv('DATABASE_URL', 'sqlite:///./data/todo.db')

engine = create_engine(
    database_url,
    echo=False,
    connect_args={'check_same_thread': False} if 'sqlite' in database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError('Database not initialized. Call create_app() first.')
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        AbstractModel.metadata.create_all(bind=engine)
        yield
        engine.dispose()

    app = FastAPI(
        title='ToDo Service',
        description='CRUD operations for todo items',
        version='1.0.0',
        lifespan=lifespan
    )

    from app.routes import router
    app.include_router(router)

    return app
