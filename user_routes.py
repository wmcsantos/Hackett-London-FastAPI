from fastapi import Depends, APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from .database import get_db
from .models import Users
from .schemas import UpdateUserRequest, UpdateUserPasswordRequest
from .auth_routes import get_current_user

user_router = APIRouter(
    prefix = '/users',
    tags = ['users']
)

@user_router.put("/me", response_model=UpdateUserRequest)
def update_user(
    data: UpdateUserRequest, 
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

@user_router.put("/me/password")
def update_user_password(
    data: UpdateUserPasswordRequest, 
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user = db.query(Users).filter(Users.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Verify current password
    if not bcrypt.verify(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail='Incorrect current password')
    
    # Verify new password
    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail='New password does not match with the confirmation')
    
    # Hash the new password
    user.password_hash = bcrypt.hash(data.new_password)

    db.commit()

    return {'message': 'Password updated successfully'}