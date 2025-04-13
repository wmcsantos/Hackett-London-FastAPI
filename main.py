from fastapi import FastAPI, Depends
from .database import init_db
from sqlalchemy.orm import Session
from .auth_routes import auth_router
from .user_routes import user_router
from .product_routes import product_router
from .category_routes import category_router
from .subcategory_routes import subcategory_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

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

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(subcategory_router)