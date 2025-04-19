from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from .database import get_db
from .models import Orders, Users
from .schemas import OrderResponse
from .auth_routes import get_current_user

order_router = APIRouter(
    prefix = '/orders',
    tags = ['orders']
)

@order_router.get("/me", response_model=List[OrderResponse])
def get_orders_by_user_id(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    orders = (
        db.query(
            Orders.id,
            Orders.order_status,
            Orders.order_date,
            Orders.total_amount
        )
        .filter(Orders.user_id == user.id)
        .all()
    )
    
    if not orders:
        HTTPException(status_code=404, detail="User does not have any completed orders")

    return orders