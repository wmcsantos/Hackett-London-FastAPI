from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from .database import get_db
from .models import Carts, Users, CartItems
from .schemas import CartResponse, CartItemsResponse
from .auth_routes import get_current_user

cart_router = APIRouter(
    prefix = '/carts',
    tags = ['carts']
)

@cart_router.get("/cart", response_model=CartResponse)
def get_user_ctive_cart(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user_active_cart = db.query(Carts).filter(Carts.user_id == current_user.id, Carts.cart_status == 'active').first()

    return user_active_cart

@cart_router.get("/cart/{cart_id}/cart-items", response_model=List[CartItemsResponse])
def get_cart_items_from_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):
    cart_items = (
        db.query(
            CartItems.cart_id,
            CartItems.product_variant_id,
            CartItems.quantity,
            CartItems.price
        )
        .filter(CartItems.cart_id == cart_id)
        .all()
    )

    return cart_items

@cart_router.get("/cart/{cart_id}/cart-items/count")
def count_cart_items(
    cart_id: int,
    db: Session = Depends(get_db)
):
    total_cart_items = db.query(func.sum(CartItems.quantity)).filter(CartItems.cart_id == cart_id).scalar()
    
    return {"total_cart_items": total_cart_items or 0}

@cart_router.post("/cart")
def create_cart(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    existing_cart = db.query(Carts).filter(Carts.user_id == current_user.id, Carts.cart_status == 'active').first()

    if existing_cart:
        return HTTPException(status_code=200, detail='An existing active cart for the logged in user already exists!')
    
    new_cart = Carts(
        user_id = current_user.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(new_cart)
    db.commit()

    return HTTPException(status_code=201, detail='Active cart created for the logged in user')

@cart_router.put("/cart/{cart_id}/cart-status", response_model=CartResponse)
def update_cart_status(
    cart_id: int,
    db: Session = Depends(get_db)
):
    cart_status_to_update = db.query(Carts).filter(Carts.id == cart_id).first()

    if not cart_status_to_update:
        raise HTTPException(status_code=404, detail='Cart does not exist')
    
    if cart_status_to_update.cart_status == 'inactive':
        raise HTTPException(status_code=200, detail='The cart is already inactive')

    cart_status_to_update.cart_status = 'inactive'

    db.commit()

    return cart_status_to_update
