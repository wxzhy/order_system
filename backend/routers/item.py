from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session

from backend.dependencies import SessionDep, CurrentUser, CurrentVendor
from backend.models import Item, Store, UserType, StoreState
from backend.schemas import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    PageResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)

router = APIRouter(prefix="/item", tags=["餐点管理"])


def populate_item_response(item: Item, session: Session) -> ItemResponse:
    """填充餐点响应数据，包括商家名"""
    item_response = ItemResponse.model_validate(item)

    # 查询商家名
    store = session.get(Store, item.store_id)
    if store:
        item_response.store_name = store.name

    return item_response


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_create: ItemCreate, current_vendor: CurrentVendor, session: SessionDep
):
    """商家添加餐点信息"""
    # 验证商家是否拥有该店铺
    store = session.get(Store, item_create.store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    if store.owner_id != current_vendor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限为该商家添加餐点"
        )

    # 检查商家是否已通过审核
    if store.state != StoreState.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商家信息未通过审核，无法添加餐点",
        )

    # 创建餐点
    db_item = Item(**item_create.model_dump(by_alias=True))
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return populate_item_response(db_item, session)


@router.get("/", response_model=PageResponse[ItemResponse])
async def list_items(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    store_id: int | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
):
    """查询餐点列表（支持多条件搜索和筛选）"""
    from sqlalchemy import func, or_

    statement = select(Item)
    count_statement = select(func.count()).select_from(Item)

    # 按商家筛选
    if store_id:
        statement = statement.where(Item.store_id == store_id)
        count_statement = count_statement.where(Item.store_id == store_id)

    # 按餐点名称或描述搜索
    if search:
        search_condition = or_(
            Item.name.like(f"%{search}%"),  # type: ignore
            Item.description.like(f"%{search}%") if Item.description else False,  # type: ignore
        )
        statement = statement.where(search_condition)
        count_statement = count_statement.where(search_condition)

    # 按价格范围筛选
    if min_price is not None:
        statement = statement.where(Item.price >= min_price)
        count_statement = count_statement.where(Item.price >= min_price)
    if max_price is not None:
        statement = statement.where(Item.price <= max_price)
        count_statement = count_statement.where(Item.price <= max_price)

    # 按库存状态筛选
    if in_stock is not None:
        if in_stock:
            statement = statement.where(Item.quantity > 0)
            count_statement = count_statement.where(Item.quantity > 0)
        else:
            statement = statement.where(Item.quantity == 0)
            count_statement = count_statement.where(Item.quantity == 0)

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    items = list(session.exec(statement).all())

    # 填充餐点响应数据
    result = [populate_item_response(item, session) for item in items]

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.get("/store/{store_id}", response_model=PageResponse[ItemResponse])
async def list_store_items(
    store_id: int,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """查询指定商家的餐点列表"""
    from sqlalchemy import func

    # 验证商家是否存在
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    statement = select(Item).where(Item.store_id == store_id)
    count_statement = (
        select(func.count()).select_from(Item).where(Item.store_id == store_id)
    )

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    items = list(session.exec(statement).all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    # 填充商家名
    items_with_store_name = [populate_item_response(item, session) for item in items]

    return PageResponse(
        records=items_with_store_name, total=total, current=current, size=limit
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, session: SessionDep):
    """查询指定餐点信息"""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="餐点不存在")
    return populate_item_response(item, session)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新餐点信息（商家本人或管理员）"""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="餐点不存在")

    # 获取商家信息验证权限
    store = session.get(Store, item.store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 验证权限：只有商家本人或管理员可以修改
    if current_user.user_type != UserType.ADMIN and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改该餐点信息"
        )

    # 更新餐点信息
    update_data = item_update.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return populate_item_response(item, session)


@router.delete("/{item_id}")
async def delete_item(item_id: int, current_user: CurrentUser, session: SessionDep):
    """删除餐点信息（商家本人或管理员）"""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="餐点不存在")

    # 获取商家信息验证权限
    store = session.get(Store, item.store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 验证权限：只有商家本人或管理员可以删除
    if current_user.user_type != UserType.ADMIN and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该餐点信息"
        )

    # TODO: 检查是否有未完成的订单包含该餐点

    session.delete(item)
    session.commit()
    return {"message": "餐点已删除"}


@router.post("/batch-delete", response_model=BatchDeleteResponse)
async def batch_delete_items(
    batch_request: BatchDeleteRequest, session: SessionDep, current_user: CurrentUser
):
    """批量删除餐点（商家或管理员）"""
    success_count = 0
    failed_count = 0
    failed_ids = []

    for item_id in batch_request.ids:
        try:
            item = session.get(Item, item_id)
            if not item:
                failed_count += 1
                failed_ids.append(item_id)
                continue

            # 获取商家信息验证权限
            store = session.get(Store, item.store_id)
            if not store:
                failed_count += 1
                failed_ids.append(item_id)
                continue

            # 验证权限：只有商家本人或管理员可以删除
            if (
                current_user.user_type != UserType.ADMIN
                and store.owner_id != current_user.id
            ):
                failed_count += 1
                failed_ids.append(item_id)
                continue

            session.delete(item)
            success_count += 1
        except Exception:
            failed_count += 1
            failed_ids.append(item_id)
            # 如果发生错误，回滚当前事务
            session.rollback()

    # 提交所有成功的删除操作
    if success_count > 0:
        session.commit()

    return BatchDeleteResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"成功删除 {success_count} 个餐点，失败 {failed_count} 个",
    )
