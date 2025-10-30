from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from backend.dependencies import SessionDep, CurrentUser, CurrentAdmin, CurrentVendor
from backend.models import Store, StoreState, UserType
from backend.schemas import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    StoreReview,
    PageResponse,
)

router = APIRouter(prefix="/store", tags=["商家管理"])


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    store_create: StoreCreate, current_user: CurrentUser, session: SessionDep
):
    """商家用户发布商家信息（需要审核）"""
    # 验证用户是否为商家
    if current_user.user_type != UserType.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只有商家用户可以发布商家信息"
        )

    # 检查商家是否已经发布过商家信息
    statement = select(Store).where(Store.owner_id == current_user.id)
    existing_store = session.exec(statement).first()
    if existing_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经发布过商家信息，请更新现有信息",
        )

    # 创建商家信息
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户ID不存在",
        )

    db_store = Store(
        **store_create.model_dump(by_alias=True),
        owner_id=current_user.id,
        state=StoreState.PENDING,
    )
    session.add(db_store)
    session.commit()
    session.refresh(db_store)
    return db_store


@router.get("/", response_model=PageResponse[StoreResponse])
async def list_stores(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    state: StoreState | None = None,
    search: str | None = None,
    owner_id: int | None = None,
):
    """查询商家列表（所有用户可见，支持搜索）"""
    from sqlalchemy import func, or_

    statement = select(Store)
    count_statement = select(func.count()).select_from(Store)

    # 非管理员只能查看已审核通过的商家
    # 注意：这里需要从请求上下文获取当前用户，简化处理，只返回APPROVED状态
    if state:
        statement = statement.where(Store.state == state)
        count_statement = count_statement.where(Store.state == state)
    else:
        # 默认只显示审核通过的商家
        statement = statement.where(Store.state == StoreState.APPROVED)
        count_statement = count_statement.where(Store.state == StoreState.APPROVED)

    # 按商家名称或描述搜索
    if search:
        search_condition = or_(
            Store.name.like(f"%{search}%"),  # type: ignore
            Store.description.like(f"%{search}%") if Store.description else False,  # type: ignore
            Store.address.like(f"%{search}%"),  # type: ignore
        )
        statement = statement.where(search_condition)
        count_statement = count_statement.where(search_condition)

    # 按店主ID筛选（用于管理后台）
    if owner_id:
        statement = statement.where(Store.owner_id == owner_id)
        count_statement = count_statement.where(Store.owner_id == owner_id)

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    stores = list(session.exec(statement).all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=stores, total=total, current=current, size=limit)


@router.get("/my", response_model=StoreResponse)
async def get_my_store(current_vendor: CurrentVendor, session: SessionDep):
    """商家查询自己的商家信息"""
    statement = select(Store).where(Store.owner_id == current_vendor.id)
    store = session.exec(statement).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="您还未发布商家信息"
        )
    return store


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(store_id: int, session: SessionDep):
    """查询指定商家信息"""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")
    return store


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int,
    store_update: StoreUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新商家信息（商家本人或管理员）"""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 验证权限：只有商家本人或管理员可以修改
    if current_user.user_type != UserType.ADMIN and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改该商家信息"
        )

    # 更新商家信息
    update_data = store_update.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(store, key, value)

    # 如果不是管理员修改，需要重新审核
    if current_user.user_type != UserType.ADMIN:
        store.state = StoreState.PENDING
        store.review_time = None

    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.delete("/{store_id}")
async def delete_store(store_id: int, current_user: CurrentUser, session: SessionDep):
    """删除商家信息（商家本人或管理员）"""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 验证权限：只有商家本人或管理员可以删除
    if current_user.user_type != UserType.ADMIN and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该商家信息"
        )

    session.delete(store)
    session.commit()
    return {"message": "商家信息已删除"}


# ============ 管理员功能 ============
@router.get("/admin/pending", response_model=PageResponse[StoreResponse])
async def list_pending_stores(
    session: SessionDep,
    current_admin: CurrentAdmin,
    skip: int = 0,
    limit: int = 100,
):
    """管理员查询待审核的商家列表"""
    from sqlalchemy import func

    statement = select(Store).where(Store.state == StoreState.PENDING)
    count_statement = (
        select(func.count()).select_from(Store).where(Store.state == StoreState.PENDING)
    )

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    stores = list(session.exec(statement).all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=stores, total=total, current=current, size=limit)


@router.post("/{store_id}/review", response_model=StoreResponse)
async def review_store(
    store_id: int, review: StoreReview, current_admin: CurrentAdmin, session: SessionDep
):
    """管理员审核商家信息"""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 更新审核状态
    store.state = review.state
    store.review_time = datetime.utcnow()

    session.add(store)
    session.commit()
    session.refresh(store)

    # TODO: 发送审核结果通知给商家

    return store
