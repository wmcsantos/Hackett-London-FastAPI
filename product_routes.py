from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from .database import get_db
from .models import ProductVariants, Sizes, ColorProducts, Colors, Products, ProductImages, Categories, t_category_products
from .schemas import ProductVariantResponse, ProductsByCategoryResponse, ProductDetailResponse, ProductImageResponse, ProductColorResponse, ProductSizeResponse

product_router = APIRouter(
    prefix = '/products',
    tags = ['products']
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

@product_router.get("/category/{id}", response_model=list[ProductsByCategoryResponse])
def get_products_by_category(id: int, db: Session = Depends(get_db)):
    products = (
        db.query(
            ProductImages.position,
            ProductImages.image_url,
            ColorProducts.product_id,
            Colors.code,
            Colors.image_url,
            Products.name,
            ProductVariants.price,
            Categories.id,
            Categories.name
        )
        .distinct(ColorProducts.product_id, Categories.id, Colors.code)
        .outerjoin(ColorProducts, ProductImages.color_products_id == ColorProducts.id)
        .outerjoin(Colors, Colors.id == ColorProducts.color_id)
        .outerjoin(Products, Products.id == ColorProducts.product_id)
        .outerjoin(ProductVariants, ProductVariants.product_id == ColorProducts.product_id)
        .outerjoin(t_category_products, t_category_products.c.product_id == ColorProducts.product_id)
        .outerjoin(Categories, Categories.id == t_category_products.c.category_id)
        .filter(ProductImages.position == 1, Categories.id == id)
        .all()
    )

    return [
        ProductsByCategoryResponse(
            position=p[0],
            image_url=p[1],
            product_id=p[2],
            color_code=p[3],
            color_image_url=p[4],
            product_name=p[5],
            price=p[6],
            category_id=p[7],
            category_name=p[8]
        )
        for p in products
    ]

@product_router.get("/product/{id}", response_model=list[ProductDetailResponse])
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = (
        db.query(
            Products.id,
            Products.name,
            Products.description_details,
            Products.description_composition,
            Products.description_care,
            Products.description_delivery,
            ProductVariants.id.label("product_variant_id"),
            ProductVariants.price
        )
        .join(ProductVariants, Products.id == ProductVariants.product_id)
        .filter(Products.id == id)
        .all()
    )

    if not product:
        raise(HTTPException(status_code=404, detail="Product not found"))

    return product

@product_router.get("/product-images", response_model=list[ProductImageResponse])
def get_product_images(color_code: str, product_id: int, db: Session = Depends(get_db)):
    product_images = (
        db.query(
            ProductImages.id,
            ProductImages.image_url,
            ProductImages.position,
            Colors.code
        )
        .join(ColorProducts, ProductImages.color_products_id == ColorProducts.id)
        .join(Colors, ColorProducts.color_id == Colors.id)
        .filter(Colors.code == color_code, ColorProducts.product_id == product_id)
        .order_by(ProductImages.position.asc())
        .all()
    )

    if not product_images:
        raise HTTPException(status_code=404, detail="No product images found")
    
    return product_images

@product_router.get("/product-colors", response_model=list[ProductColorResponse])
def get_product_colors(product_id: int, db: Session = Depends(get_db)):
    product_colors = (
        db.query(
            Colors.name,
            Colors.code,
            Colors.image_url,
            ColorProducts.color_id
        )
        .join(ColorProducts, ColorProducts.color_id == Colors.id)
        .filter(ColorProducts.product_id == product_id)
        .all()
    )

    if not product_colors:
        raise HTTPException(status_code=404, detail="No product colors found")
    
    return product_colors

@product_router.get("/product-sizes", response_model=list[ProductSizeResponse])
def get_product_sizes(color_code: str, product_id: int, db: Session = Depends(get_db)):
    product_sizes = (
        db.query(
            ProductVariants.size_id,
            Sizes.name,
            ProductVariants.stock
        )
        .join(Sizes, Sizes.id == ProductVariants.size_id)
        .join(ColorProducts, ProductVariants.color_products_id == ColorProducts.id)
        .join(Colors, ColorProducts.color_id == Colors.id)
        .filter(Colors.code == color_code, ColorProducts.product_id == product_id)
        .order_by(ProductVariants.size_id.asc())
        .all()
    )

    if not product_sizes:
        raise HTTPException(status_code=404, detail="No product sizes found")
    
    return product_sizes