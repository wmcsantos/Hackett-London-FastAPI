from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from .database import get_db
from .models import Carts, Users, CartItems
from .schemas import CartResponse, CartItemsResponse, AddItemToCartRequest
from .auth_routes import get_current_user

cart_item_router = APIRouter(
    prefix = '/cart-items',
    tags = ['cart-items']
)

@cart_item_router.post("/", response_model=CartItemsResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    cart_id: int,
    item: AddItemToCartRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    cart_item = CartItems(
        cart_id=cart_id,
        product_variant_id=item.product_variant_id,
        quantity=item.quantity,
        price=item.price
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item
