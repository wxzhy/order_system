from datetime import datetime
import asyncio
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dependencies import (
    SessionDep,
    CurrentUser,
    CurrentVendor,
    CurrentCustomer,
)
from models import (
    Order,
    OrderItem,
    Item,
    Store,
    OrderState,
    UserType,
    User,
    StoreState,
)
from schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderItemResponse,
    PageResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)

router = APIRouter(prefix="/order", tags=["订单管理"])


async def populate_order_response(order: Order, session: AsyncSession) -> OrderResponse:
    """填充订单响应数据，包括菜品名称、用户名、商家名和总金额"""
    order_response = OrderResponse.model_validate(order)

    # 查询用户名
    user = await session.get(User, order.user_id)
    if user:
        order_response.user_name = user.username

    # 查询商家名
    store = await session.get(Store, order.store_id)
    if store:
        order_response.store_name = store.name

    # 填充订单项的菜品名称
    items_with_names = []
    total_amount = 0.0

    for order_item in order.items:
        item_response = OrderItemResponse.model_validate(order_item)
        # 查询菜品名称
        item = await session.get(Item, order_item.item_id)
        if item:
            item_response.item_name = item.name
        total_amount += order_item.item_price * order_item.quantity
        items_with_names.append(item_response)

    order_response.items = items_with_names
    order_response.total_amount = total_amount

    return order_response


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_create: OrderCreate, current_customer: CurrentCustomer, session: SessionDep
):
    """普通用户创建订单"""
    # 验证商家是否存在
    store = await session.get(Store, order_create.store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 验证所有餐点是否存在且库存充足
    total_amount = 0.0
    order_items_data = []

    for item_data in order_create.items:
        item = await session.get(Item, item_data.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"餐点 {item_data.item_id} 不存在",
            )

        # 验证餐点是否属于该商家
        if item.store_id != order_create.store_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"餐点 {item.name} 不属于该商家",
            )

        # 验证库存
        if item.quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"餐点 {item.name} 库存不足，当前库存: {item.quantity}",
            )

        # 计算金额
        item_total = item.price * item_data.quantity
        total_amount += item_total

        order_items_data.append(
            {
                "item_id": item.id,
                "quantity": item_data.quantity,
                "item_price": item.price,
            }
        )

    # 创建订单
    if current_customer.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户ID不存在",
        )

    db_order = Order(
        user_id=current_customer.id,
        store_id=order_create.store_id,
        state=OrderState.PENDING,
    )
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)

    # 确保订单ID存在
    if db_order.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单创建失败",
        )

    # 创建订单项
    for item_data in order_items_data:
        order_item = OrderItem(order_id=db_order.id, **item_data)
        session.add(order_item)

        # 减少库存
        item = await session.get(Item, item_data["item_id"])
        if item:
            item.quantity -= item_data["quantity"]
            session.add(item)

    await session.commit()

    # 重新查询订单以获取所有关系数据（包括 items 和嵌套的 item）
    statement = (
        select(Order)
        .where(Order.id == db_order.id)
        .options(selectinload(Order.items).selectinload(OrderItem.item))
    )
    result = await session.execute(statement)
    db_order = result.scalar_one()

    # 构造响应
    return await populate_order_response(db_order, session)


@router.get("/", response_model=PageResponse[OrderResponse])
async def list_orders(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    state: OrderState | None = None,
    user_name: str | None = None,
    store_name: str | None = None,
    store_id: int | None = None,
    user_id: int | None = None,
):
    """查询订单列表（支持搜索）"""
    from sqlalchemy import func

    statement = select(Order)
    count_statement = select(func.count()).select_from(Order)

    # 根据用户类型过滤订单
    if current_user.user_type == UserType.CUSTOMER:
        # 普通用户只能查看自己的订单
        statement = statement.where(Order.user_id == current_user.id)
        count_statement = count_statement.where(Order.user_id == current_user.id)
    elif current_user.user_type == UserType.VENDOR:
        # 商家查看自己店铺的订单
        store_statement = select(Store).where(Store.owner_id == current_user.id)
        store = (await session.execute(store_statement)).scalars().first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家尚未提交商家信息，请先完成商家注册",
            )
        if store.state != StoreState.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家信息未审核通过，暂无法查看订单",
            )
        statement = statement.where(Order.store_id == store.id)
        count_statement = count_statement.where(Order.store_id == store.id)
    # 管理员可以查看所有订单

    # 按状态筛选
    if state:
        statement = statement.where(Order.state == state)
        count_statement = count_statement.where(Order.state == state)

    # 按用户名搜索（模糊搜索，需要关联User表）
    if user_name:
        statement = statement.join(User, Order.user_id == User.id).where(
            User.username.like(f"%{user_name}%")
        )  # type: ignore
        count_statement = count_statement.join(User, Order.user_id == User.id).where(
            User.username.like(f"%{user_name}%")
        )  # type: ignore

    # 按商家名称搜索（模糊搜索，需要关联Store表）
    if store_name:
        statement = statement.join(Store, Order.store_id == Store.id).where(
            Store.name.like(f"%{store_name}%")
        )  # type: ignore
        count_statement = count_statement.join(Store, Order.store_id == Store.id).where(
            Store.name.like(f"%{store_name}%")
        )  # type: ignore

    # 按商家ID筛选（仅管理员，内部参数）
    if store_id and current_user.user_type == UserType.ADMIN:
        statement = statement.where(Order.store_id == store_id)
        count_statement = count_statement.where(Order.store_id == store_id)

    # 按用户ID筛选（仅管理员，内部参数）
    if user_id and current_user.user_type == UserType.ADMIN:
        statement = statement.where(Order.user_id == user_id)
        count_statement = count_statement.where(Order.user_id == user_id)

    # 获取总数
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询 - 使用 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
    statement = (
        statement.options(selectinload(Order.items).selectinload(OrderItem.item))
        .offset(skip)
        .limit(limit)
    )
    orders = list((await session.execute(statement)).scalars().all())

    # 填充订单响应数据
    result = await asyncio.gather(
        *[populate_order_response(order, session) for order in orders]
    )

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.get("/my", response_model=PageResponse[OrderResponse])
async def get_my_orders(
    session: SessionDep,
    current_customer: CurrentCustomer,
    skip: int = 0,
    limit: int = 100,
    state: OrderState | None = None,
):
    """查询当前用户的订单"""
    from sqlalchemy import func

    statement = select(Order).where(Order.user_id == current_customer.id)
    count_statement = (
        select(func.count())
        .select_from(Order)
        .where(Order.user_id == current_customer.id)
    )

    if state:
        statement = statement.where(Order.state == state)
        count_statement = count_statement.where(Order.state == state)

    # 获取总数
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询 - 使用 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
    statement = (
        statement.options(selectinload(Order.items).selectinload(OrderItem.item))
        .offset(skip)
        .limit(limit)
    )
    orders = list((await session.execute(statement)).scalars().all())

    # 填充订单响应数据
    result = await asyncio.gather(
        *[populate_order_response(order, session) for order in orders]
    )

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.get("/store/my", response_model=PageResponse[OrderResponse])
async def get_my_store_orders(
    session: SessionDep,
    current_vendor: CurrentVendor,
    skip: int = 0,
    limit: int = 100,
    state: OrderState | None = None,
):
    """商家查询自己店铺的订单"""
    from sqlalchemy import func

    # 获取商家的店铺
    store_statement = select(Store).where(Store.owner_id == current_vendor.id)
    store = (await session.execute(store_statement)).scalars().first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="您还未发布商家信息"
        )

    statement = select(Order).where(Order.store_id == store.id)
    count_statement = (
        select(func.count()).select_from(Order).where(Order.store_id == store.id)
    )

    if state:
        statement = statement.where(Order.state == state)
        count_statement = count_statement.where(Order.state == state)

    # 获取总数
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询 - 使用 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
    statement = (
        statement.options(selectinload(Order.items).selectinload(OrderItem.item))
        .offset(skip)
        .limit(limit)
    )
    orders = list((await session.execute(statement)).scalars().all())

    # 填充订单响应数据
    result = await asyncio.gather(
        *[populate_order_response(order, session) for order in orders]
    )

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, session: SessionDep, current_user: CurrentUser):
    """查询指定订单信息"""
    # 使用 select 和 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.item))
    )
    result = await session.execute(statement)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    # 验证权限
    if current_user.user_type == UserType.CUSTOMER:
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限查看该订单"
            )
    elif current_user.user_type == UserType.VENDOR:
        store_statement = select(Store).where(Store.owner_id == current_user.id)
        store = (await session.execute(store_statement)).scalars().first()
        if not store or order.store_id != store.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限查看该订单"
            )
        if store.state != StoreState.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家信息未审核通过，暂无法查看订单",
            )

    # 返回订单响应
    return await populate_order_response(order, session)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新订单状态（商家审核或用户取消）"""
    # 使用 select 和 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.item))
    )
    result = await session.execute(statement)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    # 验证权限和状态转换
    if current_user.user_type == UserType.CUSTOMER:
        # 用户只能取消待审核的订单
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改该订单"
            )
        if order.state != OrderState.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只能取消待审核的订单"
            )
        if order_update.state != OrderState.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户只能取消订单"
            )

        # 恢复库存
        for order_item in order.items:
            item = await session.get(Item, order_item.item_id)
            if item:
                item.quantity += order_item.quantity
                session.add(item)

    elif current_user.user_type == UserType.VENDOR:
        # 商家审核订单
        store_statement = select(Store).where(Store.owner_id == current_user.id)
        store = (await session.execute(store_statement)).scalars().first()
        if not store or order.store_id != store.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改该订单"
            )
        if store.state != StoreState.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家信息未审核通过，暂无法审批订单",
            )

        if order.state != OrderState.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只能审核待审核的订单"
            )

        if order_update.state == OrderState.CANCELLED:
            # 商家拒绝订单，恢复库存
            for order_item in order.items:
                item = await session.get(Item, order_item.item_id)
                if item:
                    item.quantity += order_item.quantity
                    session.add(item)

    elif current_user.user_type == UserType.ADMIN:
        # 管理员可以修改任何订单状态
        if (
            order_update.state == OrderState.CANCELLED
            and order.state != OrderState.CANCELLED
        ):
            for order_item in order.items:
                item = await session.get(Item, order_item.item_id)
                if item:
                    item.quantity += order_item.quantity
                    session.add(item)

    # 更新订单状态
    order.state = order_update.state
    if order_update.state in [
        OrderState.APPROVED,
        OrderState.COMPLETED,
        OrderState.CANCELLED,
    ]:
        order.review_time = datetime.utcnow()

    session.add(order)
    await session.commit()
    await session.refresh(order)

    # 返回订单响应
    return await populate_order_response(order, session)


@router.delete("/{order_id}")
async def delete_order(order_id: int, session: SessionDep, current_user: CurrentUser):
    """删除订单（用户删除未审核订单或管理员删除任意订单）"""
    # 使用 select 和 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.item))
    )
    result = await session.execute(statement)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    # 验证权限
    if current_user.user_type == UserType.CUSTOMER:
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该订单"
            )
        if order.state != OrderState.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只能删除待审核的订单"
            )

        # 恢复库存
        for order_item in order.items:
            item = await session.get(Item, order_item.item_id)
            if item:
                item.quantity += order_item.quantity
                session.add(item)

    elif current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该订单"
        )

    await session.delete(order)
    await session.commit()
    return {"message": "订单已删除"}


@router.post("/batch-delete", response_model=BatchDeleteResponse)
async def batch_delete_orders(
    batch_request: BatchDeleteRequest, session: SessionDep, current_user: CurrentUser
):
    """批量删除订单（管理员或用户删除自己的待审核订单）"""
    success_count = 0
    failed_count = 0
    failed_ids = []

    for order_id in batch_request.ids:
        try:
            # 使用 select 和 selectinload 预加载 items 关系，并嵌套预加载每个 OrderItem 的 item 关系
            statement = (
                select(Order)
                .where(Order.id == order_id)
                .options(selectinload(Order.items).selectinload(OrderItem.item))
            )
            result = await session.execute(statement)
            order = result.scalar_one_or_none()

            if not order:
                failed_count += 1
                failed_ids.append(order_id)
                continue

            # 验证权限
            if current_user.user_type == UserType.CUSTOMER:
                # 普通用户只能删除自己的待审核订单
                if order.user_id != current_user.id:
                    failed_count += 1
                    failed_ids.append(order_id)
                    continue
                if order.state != OrderState.PENDING:
                    failed_count += 1
                    failed_ids.append(order_id)
                    continue

                # 恢复库存
                for order_item in order.items:
                    item = await session.get(Item, order_item.item_id)
                    if item:
                        item.quantity += order_item.quantity
                        session.add(item)

            elif current_user.user_type != UserType.ADMIN:
                # 商家不能删除订单
                failed_count += 1
                failed_ids.append(order_id)
                continue

            await session.delete(order)
            success_count += 1
        except Exception:
            failed_count += 1
            failed_ids.append(order_id)
            # 如果发生错误，回滚当前事务
            await session.rollback()

    # 提交所有成功的删除操作
    if success_count > 0:
        await session.commit()

    return BatchDeleteResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"成功删除 {success_count} 个订单，失败 {failed_count} 个",
    )
