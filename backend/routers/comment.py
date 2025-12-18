import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import SessionDep, CurrentUser, CurrentAdmin, CurrentCustomer
from ..models import Comment, Store, CommentState, UserType, User
from ..schemas import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentReview,
    PageResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)

router = APIRouter(prefix="/comment", tags=["评论管理"])


async def populate_comment_response(
    comment: Comment, session: AsyncSession
) -> CommentResponse:
    """填充评论响应数据，包括用户名和商家名"""
    comment_response = CommentResponse.model_validate(comment)

    # 查询用户名
    user = await session.get(User, comment.user_id)
    if user:
        comment_response.user_name = user.username

    # 查询商家名
    store = await session.get(Store, comment.store_id)
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
    store = await session.get(Store, comment_create.store_id)
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
    await session.commit()
    await session.refresh(db_comment)
    return await populate_comment_response(db_comment, session)


@router.get("/", response_model=PageResponse[CommentResponse])
async def list_comments(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    store_id: int | None = None,
    user_id: int | None = None,
    state: CommentState | None = None,
    user_name: str | None = None,
    store_name: str | None = None,
    content: str | None = None,
):
    """查询评论列表（默认只显示审核通过的，支持搜索）"""
    from sqlalchemy import func

    statement = select(Comment)
    count_statement = select(func.count()).select_from(Comment)

    # 按商家筛选（内部参数）
    if store_id:
        statement = statement.where(Comment.store_id == store_id)
        count_statement = count_statement.where(Comment.store_id == store_id)

    # 按用户筛选（内部参数）
    if user_id:
        statement = statement.where(Comment.user_id == user_id)
        count_statement = count_statement.where(Comment.user_id == user_id)

    # 按状态筛选
    if state:
        statement = statement.where(Comment.state == state)
        count_statement = count_statement.where(Comment.state == state)
    else:
        # 默认只显示审核通过的评论
        statement = statement.where(Comment.state == CommentState.APPROVED)
        count_statement = count_statement.where(Comment.state == CommentState.APPROVED)

    # 按用户名搜索（模糊搜索，需要关联User表）
    if user_name:
        statement = statement.join(User, Comment.user_id == User.id).where(
            User.username.like(f"%{user_name}%")
        )  # type: ignore
        count_statement = count_statement.join(User, Comment.user_id == User.id).where(
            User.username.like(f"%{user_name}%")
        )  # type: ignore

    # 按商家名称搜索（模糊搜索，需要关联Store表）
    if store_name:
        statement = statement.join(Store, Comment.store_id == Store.id).where(
            Store.name.like(f"%{store_name}%")
        )  # type: ignore
        count_statement = count_statement.join(
            Store, Comment.store_id == Store.id
        ).where(Store.name.like(f"%{store_name}%"))  # type: ignore

    # 按评论内容搜索（模糊搜索）
    if content:
        statement = statement.where(Comment.content.like(f"%{content}%"))  # type: ignore
        count_statement = count_statement.where(Comment.content.like(f"%{content}%"))  # type: ignore

    # 获取总数
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list((await session.execute(statement)).scalars().all())

    # 填充评论响应数据
    result = await asyncio.gather(
        *[populate_comment_response(comment, session) for comment in comments]
    )

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
    store = await session.get(Store, store_id)
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
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list((await session.execute(statement)).scalars().all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    # 填充用户名和商家名
    comments_with_names = await asyncio.gather(
        *[populate_comment_response(comment, session) for comment in comments]
    )

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
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list((await session.execute(statement)).scalars().all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    # 填充用户名和商家名
    comments_with_names = await asyncio.gather(
        *[populate_comment_response(comment, session) for comment in comments]
    )

    return PageResponse(
        records=comments_with_names, total=total, current=current, size=limit
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, session: SessionDep):
    """查询指定评论信息"""
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return await populate_comment_response(comment, session)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """更新评论内容（仅评论作者本人）"""
    comment = await session.get(Comment, comment_id)
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
    await session.commit()
    await session.refresh(comment)
    return await populate_comment_response(comment, session)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int, current_user: CurrentUser, session: SessionDep
):
    """删除评论（评论作者或管理员）"""
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 验证权限：只有评论作者本人或管理员可以删除
    if comment.user_id != current_user.id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除该评论"
        )

    await session.delete(comment)
    await session.commit()
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
            comment = await session.get(Comment, comment_id)
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

            await session.delete(comment)
            success_count += 1
        except Exception:
            failed_count += 1
            failed_ids.append(comment_id)
            # 如果发生错误，回滚当前事务
            await session.rollback()

    # 提交所有成功的删除操作
    if success_count > 0:
        await session.commit()

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
    user_name: str | None = None,
    store_name: str | None = None,
    content: str | None = None,
):
    """管理员查询待审核的评论列表"""
    from sqlalchemy import func

    statement = select(Comment).where(Comment.state == CommentState.PENDING)
    count_statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.state == CommentState.PENDING)
    )

    # 按用户名搜索（模糊搜索，需要关联User表）
    if user_name:
        statement = statement.join(User, Comment.user_id == User.id).where(
            User.username.like(f"%{user_name}%")
        )  # type: ignore
        count_statement = count_statement.join(User, Comment.user_id == User.id).where(
            User.username.like(f"%{user_name}%")
        )  # type: ignore

    # 按商家名称搜索（模糊搜索，需要关联Store表）
    if store_name:
        statement = statement.join(Store, Comment.store_id == Store.id).where(
            Store.name.like(f"%{store_name}%")
        )  # type: ignore
        count_statement = count_statement.join(
            Store, Comment.store_id == Store.id
        ).where(Store.name.like(f"%{store_name}%"))  # type: ignore

    # 按评论内容搜索（模糊搜索）
    if content:
        statement = statement.where(Comment.content.like(f"%{content}%"))  # type: ignore
        count_statement = count_statement.where(Comment.content.like(f"%{content}%"))  # type: ignore

    # 获取总数
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    comments = list((await session.execute(statement)).scalars().all())

    # 填充评论响应数据
    result = await asyncio.gather(
        *[populate_comment_response(comment, session) for comment in comments]
    )

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
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 更新审核状态
    comment.state = review.state
    comment.review_time = datetime.utcnow()

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    # TODO: 发送审核结果通知给用户

    return await populate_comment_response(comment, session)
