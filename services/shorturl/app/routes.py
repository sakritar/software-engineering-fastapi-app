import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app import get_db
from app.models import ShortUrl
from app.schemas import ShortenRequest, ShortenResponse, ShortUrlStats

router = APIRouter()

ALPHABET = string.ascii_letters + string.digits
SHORT_ID_LENGTH = 8


def generate_short_id() -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(SHORT_ID_LENGTH))


@router.post('/shorten', response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    try:
        max_attempts = 10
        for _ in range(max_attempts):
            short_id = generate_short_id()
            existing = db.query(ShortUrl).filter(ShortUrl.short_id == short_id).first()  # noqa
            if existing is None:
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique short ID"
            )

        short_url = ShortUrl(
            short_id=short_id,
            full_url=request.url
        )

        db.add(short_url)
        db.commit()
        db.refresh(short_url)
        
        return ShortenResponse(
            short_id=short_id,
            short_url=request.url
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create short URL"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get('/stats/{short_id}', response_model=ShortUrlStats, status_code=status.HTTP_200_OK)
def get_stats(short_id: str, db: Session = Depends(get_db)):
    try:
        short_url = db.query(ShortUrl).filter(ShortUrl.short_id == short_id).first()  # noqa
        if short_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Short URL not found'
            )
        return short_url
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get('/{short_id}', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
def redirect_url(short_id: str, db: Session = Depends(get_db)):
    try:
        short_url = db.query(ShortUrl).filter(ShortUrl.short_id == short_id).first()  # noqa
        if short_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Short URL not found'
            )
        return RedirectResponse(url=short_url.full_url, status_code=301)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
