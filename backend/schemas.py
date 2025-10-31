from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, EmailStr, Field
from backend.models import UserType, StoreState, OrderState, CommentState


# ============ Generic Pagination Response ============
T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    """通用分页响应模型"""

    records: List[T]
    total: int
    current: int
    size: int

    class Config:
        from_attributes = True


# ============ Generic Batch Delete Request ============
class BatchDeleteRequest(BaseModel):
    """通用批量删除请求模型"""

    ids: List[int] = Field(..., min_length=1, description="要删除的ID列表")


class BatchDeleteResponse(BaseModel):
    """批量删除响应模型"""

    success_count: int = Field(..., description="成功删除的数量")
    failed_count: int = Field(default=0, description="删除失败的数量")
    failed_ids: List[int] = Field(default_factory=list, description="删除失败的ID列表")
    message: str = Field(..., description="操作结果消息")


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
    owner_name: Optional[str] = None  # 店主名称

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
    store_name: Optional[str] = None  # 商家名称

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
    item_name: Optional[str] = None  # 菜品名称
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
    user_name: Optional[str] = None  # 用户名称
    store_id: int
    store_name: Optional[str] = None  # 商家名称
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
    user_name: Optional[str] = None  # 用户名称
    store_name: Optional[str] = None  # 商家名称

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
