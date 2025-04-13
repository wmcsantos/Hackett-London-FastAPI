from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from .database import get_db
from .models import Users
from .schemas import UpdateUserRequest
from .auth_routes import get_current_user

user_router = APIRouter(
    prefix = '/users',
    tags = ['users']
)

@user_router.put("/me", response_model=UpdateUserRequest)
def update_user(
    data: UpdateUserRequest , 
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user = db.query(Users).filter(Users.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user