from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session

from backend.dependencies import (
    SessionDep,
    CurrentUser,
    CurrentVendor,
    CurrentCustomer,
)
from backend.models import Order, OrderItem, Item, Store, OrderState, UserType, User
from backend.schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderItemResponse,
    PageResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)

router = APIRouter(prefix="/order", tags=["订单管理"])


def populate_order_response(order: Order, session: Session) -> OrderResponse:
    """填充订单响应数据，包括菜品名称和总金额"""
    order_response = OrderResponse.model_validate(order)
    
    # 填充订单项的菜品名称
    items_with_names = []
    total_amount = 0.0
    
    for order_item in order.items:
        item_response = OrderItemResponse.model_validate(order_item)
        # 查询菜品名称
        item = session.get(Item, order_item.item_id)
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
    store = session.get(Store, order_create.store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 验证所有餐点是否存在且库存充足
    total_amount = 0.0
    order_items_data = []

    for item_data in order_create.items:
        item = session.get(Item, item_data.item_id)
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
    session.commit()
    session.refresh(db_order)

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
        item = session.get(Item, item_data["item_id"])
        if item:
            item.quantity -= item_data["quantity"]
            session.add(item)

    session.commit()
    session.refresh(db_order)

    # 构造响应
    return populate_order_response(db_order, session)


@router.get("/", response_model=PageResponse[OrderResponse])
async def list_orders(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    state: OrderState | None = None,
    search: str | None = None,
    store_id: int | None = None,
    user_id: int | None = None,
):
    """查询订单列表（支持搜索）"""
    from sqlalchemy import func, or_

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
        store = session.exec(store_statement).first()
        if store:
            statement = statement.where(Order.store_id == store.id)
            count_statement = count_statement.where(Order.store_id == store.id)
        else:
            return PageResponse(records=[], total=0, current=1, size=limit)
    # 管理员可以查看所有订单

    # 按状态筛选
    if state:
        statement = statement.where(Order.state == state)
        count_statement = count_statement.where(Order.state == state)

    # 按商家ID筛选（仅管理员）
    if store_id and current_user.user_type == UserType.ADMIN:
        statement = statement.where(Order.store_id == store_id)
        count_statement = count_statement.where(Order.store_id == store_id)

    # 按用户ID筛选（仅管理员）
    if user_id and current_user.user_type == UserType.ADMIN:
        statement = statement.where(Order.user_id == user_id)
        count_statement = count_statement.where(Order.user_id == user_id)

    # 搜索功能：通过关联的商家名称或用户名搜索
    if search:
        # 需要关联 Store 和 User 表进行搜索
        search_condition = or_(
            Store.name.like(f"%{search}%"),  # type: ignore
            User.username.like(f"%{search}%"),  # type: ignore
        )
        statement = statement.join(Store).join(User).where(search_condition)
        count_statement = count_statement.join(Store).join(User).where(search_condition)

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    orders = list(session.exec(statement).all())

    # 填充订单响应数据
    result = [populate_order_response(order, session) for order in orders]

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
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    orders = list(session.exec(statement).all())

    # 填充订单响应数据
    result = [populate_order_response(order, session) for order in orders]

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
    store = session.exec(store_statement).first()

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
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    orders = list(session.exec(statement).all())

    # 填充订单响应数据
    result = [populate_order_response(order, session) for order in orders]

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, session: SessionDep, current_user: CurrentUser):
    """查询指定订单信息"""
    order = session.get(Order, order_id)
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
        store = session.exec(store_statement).first()
        if not store or order.store_id != store.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限查看该订单"
            )

    # 返回订单响应
    return populate_order_response(order, session)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新订单状态（商家审核或用户取消）"""
    order = session.get(Order, order_id)
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
            item = session.get(Item, order_item.item_id)
            if item:
                item.quantity += order_item.quantity
                session.add(item)

    elif current_user.user_type == UserType.VENDOR:
        # 商家审核订单
        store_statement = select(Store).where(Store.owner_id == current_user.id)
        store = session.exec(store_statement).first()
        if not store or order.store_id != store.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改该订单"
            )

        if order.state != OrderState.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只能审核待审核的订单"
            )

        if order_update.state == OrderState.CANCELLED:
            # 商家拒绝订单，恢复库存
            for order_item in order.items:
                item = session.get(Item, order_item.item_id)
                if item:
                    item.quantity += order_item.quantity
                    session.add(item)

    elif current_user.user_type == UserType.ADMIN:
        # 管理员可以修改任何订单状态
        pass

    # 更新订单状态
    order.state = order_update.state
    if order_update.state in [
        OrderState.APPROVED,
        OrderState.COMPLETED,
        OrderState.CANCELLED,
    ]:
        order.review_time = datetime.utcnow()

    session.add(order)
    session.commit()
    session.refresh(order)

    # 返回订单响应
    return populate_order_response(order, session)


@router.delete("/{order_id}")
async def delete_order(order_id: int, session: SessionDep, current_user: CurrentUser):
    """删除订单（用户删除未审核订单或管理员删除任意订单）"""
    order = session.get(Order, order_id)
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
            item = session.get(Item, order_item.item_id)
            if item:
                item.quantity += order_item.quantity
                session.add(item)

    elif current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该订单"
        )

    session.delete(order)
    session.commit()
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
            order = session.get(Order, order_id)
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
                    item = session.get(Item, order_item.item_id)
                    if item:
                        item.quantity += order_item.quantity
                        session.add(item)

            elif current_user.user_type != UserType.ADMIN:
                # 商家不能删除订单
                failed_count += 1
                failed_ids.append(order_id)
                continue

            session.delete(order)
            success_count += 1
        except Exception:
            failed_count += 1
            failed_ids.append(order_id)
            # 如果发生错误，回滚当前事务
            session.rollback()

    # 提交所有成功的删除操作
    if success_count > 0:
        session.commit()

    return BatchDeleteResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"成功删除 {success_count} 个订单，失败 {failed_count} 个",
    )
