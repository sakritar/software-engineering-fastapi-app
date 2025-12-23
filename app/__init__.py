from typing import Optional, Generator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from app.models import AbstractModel

# Глобальные переменные для engine и sessionmaker
_engine = None
_SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    """Dependency для получения сессии БД"""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call create_app() first.")
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_app(conf: Optional[dict] = None) -> FastAPI:
    global _engine, _SessionLocal
    
    conf = conf or {}
    
    database_uri = conf.get('SQLALCHEMY_DATABASE_URI', SQLALCHEMY_DATABASE_URI)
    track_modifications = conf.get('SQLALCHEMY_TRACK_MODIFICATIONS', SQLALCHEMY_TRACK_MODIFICATIONS)
    
    # Создаем engine и sessionmaker
    _engine = create_engine(
        database_uri,
        echo=track_modifications,
        connect_args={"check_same_thread": False} if "sqlite" in database_uri else {}
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        AbstractModel.metadata.create_all(bind=_engine)
        yield
        # Shutdown
        _engine.dispose()

    app = FastAPI(lifespan=lifespan)

    from app.routes import router
    app.include_router(router, prefix="/api/posts", tags=["posts"])

    return app
