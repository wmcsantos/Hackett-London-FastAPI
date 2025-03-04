from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import Categories
from schemas import CategoryResponse

category_router = APIRouter(
    prefix = '/categories',
    tags = ['categories']
)

@category_router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Categories)
        .where(Categories.parent_id == 0)
        .all()
    )

    return categories

@category_router.get("/{id}", response_model=CategoryResponse)
def get_category_by_id(id: int, db: Session = Depends(get_db)):
    category = (
        db.query(Categories)
        .where(Categories.parent_id == 0)
        .filter(Categories.id == id)
        .first()
    )

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category