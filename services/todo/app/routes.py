from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List

from app import get_db
from app.models import TodoItem
from app.schemas import TodoItemCreate, TodoItemUpdate, TodoItemResponse

router = APIRouter(prefix='/api/todo', tags=['todo'])


@router.post('', response_model=TodoItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: TodoItemCreate, db: Session = Depends(get_db)):
    try:
        item = TodoItem(
            title=item_data.title,
            description=item_data.description,
            completed=item_data.completed
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
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


@router.get('', response_model=List[TodoItemResponse], status_code=status.HTTP_200_OK)
def get_items(db: Session = Depends(get_db)):
    try:
        items = db.query(TodoItem).all()
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get('/{item_id}', response_model=TodoItemResponse, status_code=status.HTTP_200_OK)
def get_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.get(TodoItem, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Item not found'
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put('/{item_id}', response_model=TodoItemResponse, status_code=status.HTTP_200_OK)
def update_item(item_id: int, item_data: TodoItemUpdate, db: Session = Depends(get_db)):
    try:
        item = db.get(TodoItem, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Item not found'
            )
        
        if item_data.title is not None:
            item.title = item_data.title
        if item_data.description is not None:
            item.description = item_data.description
        if item_data.completed is not None:
            item.completed = item_data.completed
        
        db.commit()
        db.refresh(item)
        return item
    except HTTPException:
        raise
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


@router.delete('/{item_id}', status_code=status.HTTP_200_OK)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.get(TodoItem, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Item not found'
            )
        
        db.delete(item)
        db.commit()
        
        return {'message': 'Item deleted successfully'}
    except HTTPException:
        raise
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

