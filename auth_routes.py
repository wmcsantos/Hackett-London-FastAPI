from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import Users
from .database import SessionLocal, get_db
from typing import List
from .schemas import UserResponse
from .utils.password_hash import verify_password
from .utils.jwt_generation import create_access_token, decode_access_token
from datetime import timedelta

auth_router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)

# Definition of the OAuth2 password authenticatio scheme, where /auth/login is the endpoint where users will request an access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # JWT token extracted from the request using Depends(oauth2_scheme)
    # Decoding of the token 
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Fetch the user using the email stored in the JWT token
    user = get_user_by_email(db, payload["sub"])

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

@auth_router.get("/users", response_model=List[UserResponse])
def get_users(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access not allowed")
    
    return db.query(Users).all()

@auth_router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # Fetch the user
    user = get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me")
def read_users_me(current_user: Users = Depends(get_current_user)):
    return {"email": current_user.email, "is_admin": current_user.is_admin}