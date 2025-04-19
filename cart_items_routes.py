from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from .database import get_db
from .models import Carts, Users, CartItems
from .schemas import CartResponse, CartItemsResponse
from .auth_routes import get_current_user

cart_item_router = APIRouter(
    prefix = '/cart-items',
    tags = ['cart-items']
)

@cart_item_router.post("/", response_model=CartItemsResponse)
def add_item_to_cart(
    cart_id: int,
    product_variant_id: int,
    quantity: int,
    price: float,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail='Cart not found for this user')
    
    cart_item = CartItems(
        cart_id,
        product_variant_id,
        quantity,
        price,
        created_at = datetime.now(timezone.utc)
    )

    db.add(cart_item)
    db.commit()

    return HTTPException(status_code=201, detail='New item added to the cart')
