from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from .database import get_db
from .models import Categories
from .schemas import CategoryResponse

subcategory_router = APIRouter(
    prefix = '/subcategories',
    tags = ['subcategories']
)

@subcategory_router.get("/", response_model=List[CategoryResponse])
def get_subcategories(db: Session = Depends(get_db)):
    subcategories = (
        db.query(Categories)
        .where(Categories.parent_id != 0)
        .all()
    )

    return subcategories

@subcategory_router.get("/{parent_id}", response_model=List[CategoryResponse])
def get_subcategories_by_parent_id(parent_id: int, db: Session = Depends(get_db)):

    if parent_id == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subcategory not found")
    subcategories = (
        db.query(Categories)
        .filter(Categories.parent_id == parent_id)
        .all()
    )

    if not subcategories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

    return subcategories