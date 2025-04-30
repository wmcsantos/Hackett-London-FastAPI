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
    cart_item = db.query(CartItems).filter(CartItems.cart_id == cart_id, CartItems.product_variant_id == item.product_variant_id).first()
    
    if cart_item:
        # Update existing cart item if it already exists
        cart_item.quantity += item.quantity
        db.add(cart_item)  # Make sure cart_item is added to the session
    else:
        # Create a new cart item if it doesn't exist
        new_cart_item = CartItems(
            cart_id=cart_id,
            product_variant_id=item.product_variant_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(new_cart_item)
        cart_item = new_cart_item

    try:
        db.flush()  # Flush the session to ensure changes are written to the DB
        db.refresh(cart_item)  # Refresh to get the latest state from the database
    except Exception as e:
        # Handle any errors during refresh
        print(f"Error refreshing cart item: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error refreshing cart item.")

    db.commit()  # Commit the transaction after refreshing

    return cart_item
