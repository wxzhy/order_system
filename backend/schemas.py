from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from backend.models import UserType, StoreState, OrderState, CommentState


# ============ User Schemas ============
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    user_type: UserType = UserType.CUSTOMER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class UserPasswordReset(BaseModel):
    email: EmailStr
    verification_code: str
    new_password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    create_time: datetime

    class Config:
        from_attributes = True


# ============ Store Schemas ============
class StoreBase(BaseModel):
    name: str = Field(..., alias="storeName", min_length=1, max_length=255)
    description: Optional[str] = None
    address: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=50)
    hours: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, alias="imageURL", max_length=255)


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = Field(None, alias="storeName", min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    hours: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, alias="imageURL", max_length=255)


class StoreResponse(StoreBase):
    id: int
    state: StoreState
    publish_time: datetime
    review_time: Optional[datetime] = None
    owner_id: int

    class Config:
        from_attributes = True
        populate_by_name = True


class StoreReview(BaseModel):
    state: StoreState
    review_comment: Optional[str] = None


# ============ Item Schemas ============
class ItemBase(BaseModel):
    name: str = Field(..., alias="itemName", min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="imageURL", max_length=255)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)


class ItemCreate(ItemBase):
    store_id: int


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, alias="itemName", min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="imageURL", max_length=255)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)


class ItemResponse(ItemBase):
    id: int
    store_id: int

    class Config:
        from_attributes = True
        populate_by_name = True


# ============ Order Schemas ============
class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    item_price: float
    item: Optional[ItemResponse] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    store_id: int
    items: List[OrderItemCreate] = Field(..., min_length=1)
    contact_phone: Optional[str] = None
    pickup_time: Optional[str] = None


class OrderUpdate(BaseModel):
    state: OrderState


class OrderResponse(BaseModel):
    id: int
    create_time: datetime
    review_time: Optional[datetime] = None
    state: OrderState
    user_id: int
    store_id: int
    items: List[OrderItemResponse] = []
    total_amount: Optional[float] = None

    class Config:
        from_attributes = True


# ============ Comment Schemas ============
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    store_id: int


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(CommentBase):
    id: int
    publish_time: datetime
    review_time: Optional[datetime] = None
    state: CommentState
    user_id: int

    class Config:
        from_attributes = True


class CommentReview(BaseModel):
    state: CommentState
    review_comment: Optional[str] = None


# ============ Auth Schemas ============
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str  # 可以是用户名、邮箱或手机号
    password: str
