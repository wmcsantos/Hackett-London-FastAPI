from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Users
from schemas import UserResponse
from auth_routes import auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI & Docker!"}

@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(Users).all()

app.include_router(auth_router)