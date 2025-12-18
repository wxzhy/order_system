import asyncio
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import APIRouter

from ..dependencies import SessionDep, CurrentUser
from ..models import (
    Comment,
    CommentState,
    Item,
    Order,
    OrderItem,
    OrderState,
    Store,
    StoreState,
    User,
    UserType,
)
from ..schemas import (
    AdminPersonalStats,
    CustomerPersonalStats,
    PersonalStatsResponse,
    SiteStatsResponse,
    VendorPersonalStats,
)

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/personal", response_model=PersonalStatsResponse)
async def get_personal_stats(current_user: CurrentUser, session: SessionDep):
    """Return personal statistics based on the current user role."""
    response = PersonalStatsResponse(user_type=current_user.user_type)

    if current_user.user_type == UserType.VENDOR:
        store_stmt = select(Store).where(Store.owner_id == current_user.id)
        stores = list((await session.execute(store_stmt)).scalars().all())
        store_ids = [store.id for store in stores if store.id is not None]

        store_state = stores[0].state if stores else None

        item_total = 0
        order_total = 0
        pending_total = 0

        if store_ids:
            item_total = (
                await session.execute(
                    select(func.count())
                    .select_from(Item)
                    .where(Item.store_id.in_(store_ids))
                )
            ).scalar_one()
            order_total = (
                await session.execute(
                    select(func.count())
                    .select_from(Order)
                    .where(Order.store_id.in_(store_ids))
                )
            ).scalar_one()
            pending_total = (
                await session.execute(
                    select(func.count())
                    .select_from(Order)
                    .where(
                        Order.store_id.in_(store_ids), Order.state == OrderState.PENDING
                    )
                )
            ).scalar_one()

        response.vendor = VendorPersonalStats(
            store_exists=bool(store_ids),
            store_state=store_state,
            item_total=item_total or 0,
            order_total=order_total or 0,
            order_pending=pending_total or 0,
        )

        return response

    if current_user.user_type == UserType.ADMIN:
        pending_store_review = (
            await session.execute(
                select(func.count())
                .select_from(Store)
                .where(Store.state == StoreState.PENDING)
            )
        ).scalar_one()
        pending_comment_review = (
            await session.execute(
                select(func.count())
                .select_from(Comment)
                .where(Comment.state == CommentState.PENDING)
            )
        ).scalar_one()

        response.admin = AdminPersonalStats(
            pending_store_review=pending_store_review or 0,
            pending_comment_review=pending_comment_review or 0,
        )

        return response

    order_total = (
        await session.execute(
            select(func.count())
            .select_from(Order)
            .where(Order.user_id == current_user.id)
        )
    ).scalar_one()
    pending_total = (
        await session.execute(
            select(func.count())
            .select_from(Order)
            .where(Order.user_id == current_user.id, Order.state == OrderState.PENDING)
        )
    ).scalar_one()

    response.customer = CustomerPersonalStats(
        order_total=order_total or 0, order_pending=pending_total or 0
    )

    return response


@router.get("/site", response_model=SiteStatsResponse)
async def get_site_stats(_current_user: CurrentUser, session: SessionDep):
    """Return aggregated site statistics."""
    user_total = (
        await session.execute(select(func.count()).select_from(User))
    ).scalar_one()
    merchant_total = (
        await session.execute(
            select(func.count())
            .select_from(Store)
            .where(Store.state == StoreState.APPROVED)
        )
    ).scalar_one()
    order_total = (
        await session.execute(select(func.count()).select_from(Order))
    ).scalar_one()

    turnover_stmt = (
        select(func.coalesce(func.sum(OrderItem.item_price * OrderItem.quantity), 0.0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.state.in_([OrderState.APPROVED, OrderState.COMPLETED]))
    )
    turnover_total = (await session.execute(turnover_stmt)).scalar_one()

    return SiteStatsResponse(
        user_total=user_total or 0,
        merchant_total=merchant_total or 0,
        order_total=order_total or 0,
        turnover_total=float(turnover_total or 0),
    )
