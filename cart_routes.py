from fastapi import Depends, APIRouter, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from .database import get_db
from .models import Carts, Users, CartItems, ProductVariants, Products, ProductImages, ColorProducts, Sizes, Colors
from .schemas import CartResponse, ItemsInCartResponse, AddItemToCartRequest
from .auth_routes import get_current_user
from .cart_items_routes import add_item_to_cart

cart_router = APIRouter(
    prefix = '/carts',
    tags = ['carts']
)

@cart_router.get("/cart", response_model=Optional[CartResponse])
def get_user_active_cart(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user_active_cart = db.query(Carts).filter(Carts.user_id == current_user.id, Carts.cart_status == 'active').first()

    if not user_active_cart:
        return None
        # raise HTTPException(status_code=404, detail='User does not have an active cart')

    return user_active_cart

@cart_router.get("/cart/{cart_id}/cart-items", response_model=List[ItemsInCartResponse])
def get_cart_items_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = (
        db.query(Carts)
        .filter(Carts.id == cart_id, Carts.user_id == current_user.id)
        .first()
    )
    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    cart_items = (
        db.query(CartItems, Products.name.label("product_name"), ProductImages.image_url, Colors.name.label("color"), Sizes.name.label("size"))
        .join(ProductVariants, CartItems.product_variant_id == ProductVariants.id)
        .join(Products, ProductVariants.product_id == Products.id)
        .join(ProductImages, ProductVariants.color_products_id == ProductImages.color_products_id)
        .join(ColorProducts, ProductVariants.color_products_id == ColorProducts.id)
        .join(Sizes, ProductVariants.size_id == Sizes.id)
        .join(Colors, ColorProducts.color_id == Colors.id)
        .filter(CartItems.cart_id == cart_id, ProductImages.position == 1)
        .all()
    )

    result = []
    for cart_item, product_name, image_url, color, size in cart_items:
        result.append({
            "id": cart_item.id,
            "product_name": product_name,
            "image_url": image_url,
            "color": color,
            "size": size,
            "quantity": cart_item.quantity,
            "price": cart_item.price
        })

    return result

@cart_router.delete("/cart/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    # First delete cart items
    db.query(CartItems).filter(CartItems.cart_id == cart_id).delete()
    
    db.delete(cart)
    db.commit()

    return 

@cart_router.get("/cart/{cart_id}/cart-items/count")
def count_cart_items(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    total_cart_items = db.query(func.sum(CartItems.quantity)).filter(CartItems.cart_id == cart_id).scalar()
    
    return {"total_cart_items": total_cart_items or 0}

@cart_router.post("/cart", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    existing_cart = db.query(Carts).filter(Carts.user_id == current_user.id, Carts.cart_status == 'active').first()

    if existing_cart:
        return existing_cart
    
    new_cart = Carts(
        user_id = current_user.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(new_cart)
    db.flush()

    db.commit()

    return db.query(Carts).get(new_cart.id)

@cart_router.put("/cart/{cart_id}/cart-status", response_model=CartResponse)
def update_cart_status(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    cart_status_to_update = db.query(Carts).filter(Carts.id == cart_id).first()

    if not cart_status_to_update:
        raise HTTPException(status_code=404, detail='Cart does not exist')
    
    if cart_status_to_update.cart_status == 'inactive':
        raise HTTPException(status_code=200, detail='The cart is already inactive')

    cart_status_to_update.cart_status = 'inactive'

    db.commit()

    return cart_status_to_update

@cart_router.post("/cart/add-cart-item")
def add_to_cart(
    item: AddItemToCartRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):   
    # Get user's active cart
    user_cart = get_user_active_cart(db, current_user)

    # Create a cart if none exists
    if not user_cart:
        create_cart(db, current_user)
        user_cart = get_user_active_cart(db, current_user)

    # Get all cart items for the cart
    cart_items = get_cart_items_from_cart(user_cart.id, db, current_user)

    # Check if product already exists in the cart
    for  cart_item in cart_items:
        if cart_item.product_variant_id == item.product_variant_id:
            cart_item.quantity += item.quantity
            db.commit()
            return {"message": "Item quantity updated in cart"}
    
    # if the product is not found in the cart, add the new cart item
    add_item_to_cart(cart_id=user_cart.id, item=item, db=db, current_user=current_user)
    return {"message": "Item added to cart"}