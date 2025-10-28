import enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime

# --- Enums based on document definitions ---


class UserType(str, enum.Enum):
    CUSTOMER = "customer"  # 普通用户 [cite: 34]
    VENDOR = "vendor"  # 商家用户 [cite: 34]
    ADMIN = "admin"  # 管理员用户 [cite: 34]


class StoreState(str, enum.Enum):
    PENDING = "pending"  # 待审核 [cite: 64]
    APPROVED = "approved"  # 正常营业 (审核通过) [cite: 64]
    DISABLED = "disabled"  # 已停用 [cite: 64]


class OrderState(str, enum.Enum):
    PENDING = "pending"  # 待审核 [cite: 72]
    APPROVED = "approved"  # 已同意 [cite: 72]
    COMPLETED = "completed"  # 已完成 [cite: 72]
    CANCELLED = "cancelled"  # 已取消 [cite: 72]


class CommentState(str, enum.Enum):
    PENDING = "pending"  # 未审核 [cite: 80]
    APPROVED = "approved"  # 审核通过 [cite: 80]
    REJECTED = "rejected"  # 审核未通过 [cite: 80]


# --- Link Tables ---


class OrderItem(SQLModel, table=True):
    """订单中的具体餐点项 [cite: 73]"""

    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(gt=0)
    item_price: float = Field(gt=0)  # 下单时的价格快照 [cite: 76]

    order_id: int = Field(foreign_key="order.id")
    order: "Order" = Relationship(back_populates="items")

    item_id: int = Field(foreign_key="item.id")
    item: "Item" = Relationship(back_populates="order_items")


# --- Main Tables ---


class User(SQLModel, table=True):
    """用户模型 (合并了普通用户、商家和管理员) [cite: 45, 53, 57]"""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None, unique=True, index=True)
    hashed_password: str = Field()
    user_type: UserType = Field(
        default=UserType.CUSTOMER,
        sa_column=Column(
            SQLAlchemyEnum(
                UserType,
                native_enum=False,
                values_callable=lambda x: [e.value for e in x],
            )
        ),
    )
    create_time: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stores: List["Store"] = Relationship(back_populates="owner")
    orders: List["Order"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")


class Store(SQLModel, table=True):
    """商家信息 [cite: 61]"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, alias="storeName")
    description: Optional[str] = Field(default=None)
    address: str
    phone: str
    hours: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None, alias="imageURL")
    state: StoreState = Field(
        default=StoreState.PENDING,
        sa_column=Column(
            SQLAlchemyEnum(
                StoreState,
                native_enum=False,
                values_callable=lambda x: [e.value for e in x],
            )
        ),
    )
    publish_time: datetime = Field(default_factory=datetime.utcnow)
    review_time: Optional[datetime] = Field(default=None)

    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="stores")

    # Relationships
    items: List["Item"] = Relationship(back_populates="store")
    orders: List["Order"] = Relationship(back_populates="store")
    comments: List["Comment"] = Relationship(back_populates="store")


class Item(SQLModel, table=True):
    """餐点信息 [cite: 65]"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, alias="itemName")
    description: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None, alias="imageURL")
    price: float = Field(gt=0)
    quantity: int = Field(default=0)  # 库存 [cite: 68]

    store_id: int = Field(foreign_key="store.id")
    store: Store = Relationship(back_populates="items")

    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="item")


class Order(SQLModel, table=True):
    """预约订单 [cite: 69]"""

    id: Optional[int] = Field(default=None, primary_key=True)
    create_time: datetime = Field(default_factory=datetime.utcnow)
    review_time: Optional[datetime] = Field(default=None)
    state: OrderState = Field(
        default=OrderState.PENDING,
        sa_column=Column(
            SQLAlchemyEnum(
                OrderState,
                native_enum=False,
                values_callable=lambda x: [e.value for e in x],
            )
        ),
    )

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="orders")

    store_id: int = Field(foreign_key="store.id")
    store: Store = Relationship(back_populates="orders")

    # Relationships
    items: List[OrderItem] = Relationship(back_populates="order")


class Comment(SQLModel, table=True):
    """评论 [cite: 77]"""

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    publish_time: datetime = Field(default_factory=datetime.utcnow)
    review_time: Optional[datetime] = Field(default=None)
    state: CommentState = Field(
        default=CommentState.PENDING,
        sa_column=Column(
            SQLAlchemyEnum(
                CommentState,
                native_enum=False,
                values_callable=lambda x: [e.value for e in x],
            )
        ),
    )

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="comments")

    store_id: int = Field(foreign_key="store.id")
    store: Store = Relationship(back_populates="comments")
