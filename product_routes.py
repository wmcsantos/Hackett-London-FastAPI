from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import ProductVariants, Sizes, ColorProducts, Colors, Products
from schemas import ProductVariantResponse

product_router = APIRouter(
    prefix = '/product',
    tags = ['product']
)

@product_router.get("/variants", response_model=List[ProductVariantResponse])
def get_product_variants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    variants = (
        db.query(
            ProductVariants.id,
            ProductVariants.created_at,
            ProductVariants.reference2,
            ProductVariants.stock,
            ProductVariants.product_id,
            ProductVariants.price,
            ProductVariants.color_products_id,
            ProductVariants.updated_at,
            Sizes.name.label("size_name"),
            Products.name.label("product_name"),
            Colors.name.label("color")
        )
        .join(Sizes, ProductVariants.size_id == Sizes.id)
        .join(ColorProducts, ProductVariants.color_products_id == ColorProducts.id)
        .join(Products, ProductVariants.product_id == Products.id)
        .join(Colors, ColorProducts.color_id == Colors.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convert query results into dictionaries
    return variants