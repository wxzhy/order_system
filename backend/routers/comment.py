from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session

from backend.dependencies import SessionDep, CurrentUser, CurrentAdmin, CurrentCustomer
from backend.models import Comment, Store, CommentState, UserType, User
from backend.schemas import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentReview,
    PageResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)

router = APIRouter(prefix="/comment", tags=["评论管理"])


def populate_comment_response(comment: Comment, session: Session) -> CommentResponse:
    """填充评论响应数据，包括用户名和商家名"""
    comment_response = CommentResponse.model_validate(comment)

    # 查询用户名
    user = session.get(User, comment.user_id)
    if user:
        comment_response.user_name = user.username

    # 查询商家名
    store = session.get(Store, comment.store_id)
    if store:
        comment_response.store_name = store.name

    return comment_response


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_create: CommentCreate,
    current_customer: CurrentCustomer,
    session: SessionDep,
):
    """普通用户发表评论（需要审核）"""
    # 验证商家是否存在
    store = session.get(Store, comment_create.store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    # 创建评论
    if current_customer.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户ID不存在",
        )

    db_comment = Comment(
        content=comment_create.content,
        store_id=comment_create.store_id,
        user_id=current_customer.id,
        state=CommentState.PENDING,
    )
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return populate_comment_response(db_comment, session)


@router.get("/", response_model=PageResponse[CommentResponse])
async def list_comments(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    store_id: int | None = None,
    state: CommentState | None = None,
    search: str | None = None,
):
    """查询评论列表（默认只显示审核通过的，支持搜索）"""
    from sqlalchemy import func, or_

    statement = select(Comment)
    count_statement = select(func.count()).select_from(Comment)

    # 按商家筛选
    if store_id:
        statement = statement.where(Comment.store_id == store_id)
        count_statement = count_statement.where(Comment.store_id == store_id)

    # 按状态筛选
    if state:
        statement = statement.where(Comment.state == state)
        count_statement = count_statement.where(Comment.state == state)
    else:
        # 默认只显示审核通过的评论
        statement = statement.where(Comment.state == CommentState.APPROVED)
        count_statement = count_statement.where(Comment.state == CommentState.APPROVED)

    # 搜索功能：通过评论内容、商家名称或用户名搜索
    if search:
        # 需要关联 Store 和 User 表进行搜索
        search_condition = or_(
            Comment.content.like(f"%{search}%"),  # type: ignore
            Store.name.like(f"%{search}%"),  # type: ignore
            User.username.like(f"%{search}%"),  # type: ignore
        )
        statement = statement.join(Store).join(User).where(search_condition)
        count_statement = count_statement.join(Store).join(User).where(search_condition)

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list(session.exec(statement).all())

    # 填充评论响应数据
    result = [populate_comment_response(comment, session) for comment in comments]

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.get("/store/{store_id}", response_model=PageResponse[CommentResponse])
async def list_store_comments(
    store_id: int,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """查询指定商家的评论列表（只显示审核通过的）"""
    from sqlalchemy import func

    # 验证商家是否存在
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    statement = select(Comment).where(
        Comment.store_id == store_id, Comment.state == CommentState.APPROVED
    )
    count_statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.store_id == store_id, Comment.state == CommentState.APPROVED)
    )

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list(session.exec(statement).all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    # 填充用户名和商家名
    comments_with_names = [
        populate_comment_response(comment, session) for comment in comments
    ]

    return PageResponse(
        records=comments_with_names, total=total, current=current, size=limit
    )


@router.get("/my", response_model=PageResponse[CommentResponse])
async def get_my_comments(
    session: SessionDep,
    current_customer: CurrentCustomer,
    skip: int = 0,
    limit: int = 100,
):
    """查询当前用户的评论"""
    from sqlalchemy import func

    statement = select(Comment).where(Comment.user_id == current_customer.id)
    count_statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.user_id == current_customer.id)
    )

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list(session.exec(statement).all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    # 填充用户名和商家名
    comments_with_names = [
        populate_comment_response(comment, session) for comment in comments
    ]

    return PageResponse(
        records=comments_with_names, total=total, current=current, size=limit
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, session: SessionDep):
    """查询指定评论信息"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return populate_comment_response(comment, session)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新评论内容（仅评论作者本人）"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 验证权限：只有评论作者本人可以修改
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改该评论"
        )

    # 更新评论内容
    comment.content = comment_update.content
    # 修改后需要重新审核
    comment.state = CommentState.PENDING
    comment.review_time = None

    session.add(comment)
    session.commit()
    session.refresh(comment)
    return populate_comment_response(comment, session)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int, current_user: CurrentUser, session: SessionDep
):
    """删除评论（评论作者或管理员）"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 验证权限：只有评论作者本人或管理员可以删除
    if comment.user_id != current_user.id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该评论"
        )

    session.delete(comment)
    session.commit()
    return {"message": "评论已删除"}


@router.post("/batch-delete", response_model=BatchDeleteResponse)
async def batch_delete_comments(
    batch_request: BatchDeleteRequest, session: SessionDep, current_user: CurrentUser
):
    """批量删除评论（管理员或评论作者）"""
    success_count = 0
    failed_count = 0
    failed_ids = []

    for comment_id in batch_request.ids:
        try:
            comment = session.get(Comment, comment_id)
            if not comment:
                failed_count += 1
                failed_ids.append(comment_id)
                continue

            # 验证权限：只有评论作者本人或管理员可以删除
            if (
                comment.user_id != current_user.id
                and current_user.user_type != UserType.ADMIN
            ):
                failed_count += 1
                failed_ids.append(comment_id)
                continue

            session.delete(comment)
            success_count += 1
        except Exception:
            failed_count += 1
            failed_ids.append(comment_id)
            # 如果发生错误，回滚当前事务
            session.rollback()

    # 提交所有成功的删除操作
    if success_count > 0:
        session.commit()

    return BatchDeleteResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"成功删除 {success_count} 个评论，失败 {failed_count} 个",
    )


# ============ 管理员功能 ============
@router.get("/admin/pending", response_model=PageResponse[CommentResponse])
async def list_pending_comments(
    session: SessionDep,
    current_admin: CurrentAdmin,
    skip: int = 0,
    limit: int = 100,
):
    """管理员查询待审核的评论列表"""
    from sqlalchemy import func

    statement = select(Comment).where(Comment.state == CommentState.PENDING)
    count_statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.state == CommentState.PENDING)
    )

    # 获取总数
    total = session.exec(count_statement).one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list(session.exec(statement).all())

    # 填充评论响应数据
    result = [populate_comment_response(comment, session) for comment in comments]

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=result, total=total, current=current, size=limit)


@router.post("/{comment_id}/review", response_model=CommentResponse)
async def review_comment(
    comment_id: int,
    review: CommentReview,
    current_admin: CurrentAdmin,
    session: SessionDep,
):
    """管理员审核评论"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 更新审核状态
    comment.state = review.state
    comment.review_time = datetime.utcnow()

    session.add(comment)
    session.commit()
    session.refresh(comment)

    # TODO: 发送审核结果通知给用户

    return populate_comment_response(comment, session)
