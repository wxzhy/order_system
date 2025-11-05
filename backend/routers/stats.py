from sqlalchemy import func
from sqlmodel import select
from fastapi import APIRouter

from backend.dependencies import SessionDep, CurrentUser
from backend.models import (
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
from backend.schemas import (
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
        stores = list(session.exec(store_stmt).all())
        store_ids = [store.id for store in stores if store.id is not None]

        store_state = stores[0].state if stores else None

        item_total = 0
        order_total = 0
        pending_total = 0

        if store_ids:
            item_total = session.exec(
                select(func.count()).select_from(Item).where(Item.store_id.in_(store_ids))
            ).one()
            order_total = session.exec(
                select(func.count()).select_from(Order).where(Order.store_id.in_(store_ids))
            ).one()
            pending_total = session.exec(
                select(func.count())
                .select_from(Order)
                .where(Order.store_id.in_(store_ids), Order.state == OrderState.PENDING)
            ).one()

        response.vendor = VendorPersonalStats(
            store_exists=bool(store_ids),
            store_state=store_state,
            item_total=item_total or 0,
            order_total=order_total or 0,
            order_pending=pending_total or 0,
        )

        return response

    if current_user.user_type == UserType.ADMIN:
        pending_store_review = session.exec(
            select(func.count())
            .select_from(Store)
            .where(Store.state == StoreState.PENDING)
        ).one()
        pending_comment_review = session.exec(
            select(func.count())
            .select_from(Comment)
            .where(Comment.state == CommentState.PENDING)
        ).one()

        response.admin = AdminPersonalStats(
            pending_store_review=pending_store_review or 0,
            pending_comment_review=pending_comment_review or 0,
        )

        return response

    order_total = session.exec(
        select(func.count()).select_from(Order).where(Order.user_id == current_user.id)
    ).one()
    pending_total = session.exec(
        select(func.count())
        .select_from(Order)
        .where(Order.user_id == current_user.id, Order.state == OrderState.PENDING)
    ).one()

    response.customer = CustomerPersonalStats(
        order_total=order_total or 0, order_pending=pending_total or 0
    )

    return response


@router.get("/site", response_model=SiteStatsResponse)
async def get_site_stats(_current_user: CurrentUser, session: SessionDep):
    """Return aggregated site statistics."""
    user_total = session.exec(select(func.count()).select_from(User)).one()
    merchant_total = session.exec(
        select(func.count())
        .select_from(Store)
        .where(Store.state == StoreState.APPROVED)
    ).one()
    order_total = session.exec(select(func.count()).select_from(Order)).one()

    turnover_stmt = (
        select(func.coalesce(func.sum(OrderItem.item_price * OrderItem.quantity), 0.0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.state.in_([OrderState.APPROVED, OrderState.COMPLETED]))
    )
    turnover_total = session.exec(turnover_stmt).one()

    return SiteStatsResponse(
        user_total=user_total or 0,
        merchant_total=merchant_total or 0,
        order_total=order_total or 0,
        turnover_total=float(turnover_total or 0),
    )
