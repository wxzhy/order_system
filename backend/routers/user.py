from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from backend.dependencies import SessionDep, CurrentUser, CurrentAdmin
from backend.models import User
from backend.schemas import (
    UserResponse,
    UserUpdate,
    UserPasswordUpdate,
    UserPasswordReset,
)
from backend.security import verify_password, get_password_hash

router = APIRouter(prefix="/api/user", tags=["用户管理"])


@router.get("/me", response_model=UserResponse)
async def get_my_info(current_user: CurrentUser):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_info(
    user_update: UserUpdate, current_user: CurrentUser, session: SessionDep
):
    """更新当前用户信息"""
    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != current_user.email:
        statement = select(User).where(
            User.email == user_update.email, User.id != current_user.id
        )
        existing_email = session.exec(statement).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用"
            )

    # 检查用户名是否已被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        statement = select(User).where(
            User.username == user_update.username, User.id != current_user.id
        )
        existing_username = session.exec(statement).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被使用"
            )

    # 检查手机号是否已被其他用户使用
    if user_update.phone and user_update.phone != current_user.phone:
        statement = select(User).where(
            User.phone == user_update.phone, User.id != current_user.id
        )
        existing_phone = session.exec(statement).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="手机号已被使用"
            )

    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.put("/me/password")
async def update_my_password(
    password_update: UserPasswordUpdate, current_user: CurrentUser, session: SessionDep
):
    """修改当前用户密码"""
    # 验证旧密码
    if not verify_password(password_update.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误"
        )

    # 更新密码
    current_user.hashed_password = get_password_hash(password_update.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "密码修改成功"}


@router.delete("/me")
async def delete_my_account(current_user: CurrentUser, session: SessionDep):
    """注销当前用户账户"""
    session.delete(current_user)
    session.commit()
    return {"message": "账户已注销"}


# ============ 管理员功能 ============
@router.get("/", response_model=List[UserResponse])
async def list_users(
    session: SessionDep,
    current_admin: CurrentAdmin,
    skip: int = 0,
    limit: int = 100,
    user_type: str | None = None,
    search: str | None = None,
):
    """管理员查询用户列表"""
    statement = select(User)

    # 按用户类型筛选
    if user_type:
        statement = statement.where(User.user_type == user_type)

    # 按关键词搜索（用户名、邮箱、手机号）
    if search:
        from sqlalchemy import or_

        statement = statement.where(
            or_(
                User.username.like(f"%{search}%"),  # type: ignore
                User.email.like(f"%{search}%"),  # type: ignore
                User.phone.like(f"%{search}%") if User.phone else False,  # type: ignore
            )
        )

    statement = statement.offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: SessionDep, current_admin: CurrentAdmin):
    """管理员查询指定用户信息"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: SessionDep,
    current_admin: CurrentAdmin,
):
    """管理员更新指定用户信息"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != user.email:
        statement = select(User).where(
            User.email == user_update.email, User.id != user_id
        )
        existing_email = session.exec(statement).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用"
            )

    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: SessionDep, current_admin: CurrentAdmin):
    """管理员删除指定用户"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    session.delete(user)
    session.commit()
    return {"message": "用户已删除"}


@router.post("/reset-password")
async def reset_password(reset_data: UserPasswordReset, session: SessionDep):
    """找回密码（需要验证码）"""
    # 查找用户
    statement = select(User).where(User.email == reset_data.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # TODO: 这里应该验证 verification_code 是否正确
    # 目前简化处理，实际应该有验证码发送和验证逻辑

    # 更新密码
    user.hashed_password = get_password_hash(reset_data.new_password)
    session.add(user)
    session.commit()
    return {"message": "密码重置成功"}
