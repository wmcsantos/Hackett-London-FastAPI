from pydantic import BaseModel, EmailStr, Field
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

class ProductsByCategoryResponse(BaseModel):
    position: int
    image_url: str
    product_id: int
    color_code: str
    color_image_url: str
    product_name: str
    price: float
    category_id: int
    category_name: str

class CategoryResponse(BaseModel):
    id: int
    name: str

class ProductDetailResponse(BaseModel):
    id: int
    name: str
    description_details: Optional[str]
    description_composition: Optional[str]
    description_care: Optional[str]
    description_delivery: Optional[str]
    product_variant_id: int
    price: float

class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    position: int
    code: str

class ProductColorResponse(BaseModel):
    name: str
    code: str
    image_url: str
    color_id: int

class ProductSizeResponse(BaseModel):
    size_id: int
    name:str
    stock: int

class UpdateUserRequest(BaseModel):
    title: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]
    email: Optional[EmailStr]

class UpdateUserPasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_new_password: str = Field(..., min_length=6, max_length=100)

class OrderResponse(BaseModel):
    id: int
    order_status: str
    order_date: datetime.datetime
    total_amount: float

class CartResponse(BaseModel):
    id: int
    user_id: int
    cart_status: str
    session_id: Optional[str]
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

class CartItemsResponse(BaseModel):
    id: int
    cart_id: int
    product_variant_id: int
    quantity: int
    price: float
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

class ItemsInCartResponse(BaseModel):
    id: int
    product_name: str
    image_url: str
    color: str
    size: str
    quantity: int
    price: float

class AddItemToCartRequest(BaseModel):
    product_variant_id: int
    quantity: int
    price: float