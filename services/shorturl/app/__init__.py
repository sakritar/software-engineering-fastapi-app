import os
from contextlib import asynccontextmanager
from typing import Generator

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import AbstractModel

database_url = os.getenv('DATABASE_URL', 'sqlite:////app/data/shorturl.db')

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
        # Миграции выполняются через Alembic в entrypoint.sh
        yield
        engine.dispose()

    app = FastAPI(
        title="Short URL Service",
        description="URL shortening service",
        version="1.0.0",
        lifespan=lifespan
    )

    from app.routes import router
    app.include_router(router)

    return app
