from pydantic import BaseModel
import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: int
    title: str
    first_name: str
    last_name: str
    gender: str
    email: str
    is_admin: bool
    remember_token: Optional[str]
    created_at: datetime.datetime
    email_verified_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True

class ProductVariantResponse(BaseModel):
    id: int
    size_name: str
    stock: int
    product_name: str
    reference2: Optional[str]
    price: float
    color: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

class CategoryResponse(BaseModel):
    id: int
    name: str