from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from .database import get_db
from .models import Carts, Users, CartItems
from .schemas import CartResponse, CartItemsResponse, AddItemToCartRequest
from .auth_routes import get_current_user
from .cart_items_routes import add_item_to_cart

cart_router = APIRouter(
    prefix = '/carts',
    tags = ['carts']
)

@cart_router.get("/cart", response_model=CartResponse)
def get_user_active_cart(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user_active_cart = db.query(Carts).filter(Carts.user_id == current_user.id, Carts.cart_status == 'active').first()

    if not user_active_cart:
        raise HTTPException(status_code=404, detail='User does not have an active cart')

    return user_active_cart

@cart_router.get("/cart/{cart_id}/cart-items", response_model=List[CartItemsResponse])
def get_cart_items_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    cart_items = (
        db.query(CartItems)
        .filter(CartItems.cart_id == cart_id)
        .all()
    )

    return cart_items

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
    db.commit()
    db.refresh(new_cart)

    return new_cart

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

@cart_router.post("/cart/{cart_id}/add-cart-item")
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