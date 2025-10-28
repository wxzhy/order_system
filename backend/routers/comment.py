from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from backend.dependencies import SessionDep, CurrentUser, CurrentAdmin, CurrentCustomer
from backend.models import Comment, Store, CommentState, UserType
from backend.schemas import CommentCreate, CommentUpdate, CommentResponse, CommentReview

router = APIRouter(prefix="/api/comment", tags=["评论管理"])


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
    return db_comment


@router.get("/", response_model=List[CommentResponse])
async def list_comments(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    store_id: int | None = None,
    state: CommentState | None = None,
):
    """查询评论列表（默认只显示审核通过的）"""
    statement = select(Comment)

    # 按商家筛选
    if store_id:
        statement = statement.where(Comment.store_id == store_id)

    # 按状态筛选
    if state:
        statement = statement.where(Comment.state == state)
    else:
        # 默认只显示审核通过的评论
        statement = statement.where(Comment.state == CommentState.APPROVED)

    statement = statement.offset(skip).limit(limit)
    comments = session.exec(statement).all()
    return comments


@router.get("/store/{store_id}", response_model=List[CommentResponse])
async def list_store_comments(
    store_id: int,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """查询指定商家的评论列表（只显示审核通过的）"""
    # 验证商家是否存在
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商家不存在")

    statement = select(Comment).where(
        Comment.store_id == store_id, Comment.state == CommentState.APPROVED
    )
    statement = statement.offset(skip).limit(limit)
    comments = session.exec(statement).all()
    return comments


@router.get("/my", response_model=List[CommentResponse])
async def get_my_comments(
    session: SessionDep,
    current_customer: CurrentCustomer,
    skip: int = 0,
    limit: int = 100,
):
    """查询当前用户的评论"""
    statement = select(Comment).where(Comment.user_id == current_customer.id)
    statement = statement.offset(skip).limit(limit)
    comments = session.exec(statement).all()
    return comments


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, session: SessionDep):
    """查询指定评论信息"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return comment


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
    return comment


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


# ============ 管理员功能 ============
@router.get("/admin/pending", response_model=List[CommentResponse])
async def list_pending_comments(
    session: SessionDep,
    current_admin: CurrentAdmin,
    skip: int = 0,
    limit: int = 100,
):
    """管理员查询待审核的评论列表"""
    statement = select(Comment).where(Comment.state == CommentState.PENDING)
    statement = statement.offset(skip).limit(limit)
    comments = session.exec(statement).all()
    return comments


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

    return comment
