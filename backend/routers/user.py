import asyncio
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.dependencies import SessionDep, CurrentUser, CurrentAdmin
from backend.models import User
from backend.schemas import (
    UserResponse,
    AdminUserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserDeleteRequest,
    UserPasswordReset,
    PageResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)
from backend.security import verify_password, get_password_hash

router = APIRouter(prefix="/user", tags=["用户管理"])


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
        existing_email = (await session.execute(statement)).scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用"
            )

    # 检查用户名是否已被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        statement = select(User).where(
            User.username == user_update.username, User.id != current_user.id
        )
        existing_username = (await session.execute(statement)).scalars().first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被使用"
            )

    # 检查手机号是否已被其他用户使用
    if user_update.phone and user_update.phone != current_user.phone:
        statement = select(User).where(
            User.phone == user_update.phone, User.id != current_user.id
        )
        existing_phone = (await session.execute(statement)).scalars().first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="手机号已被使用"
            )

    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
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
    await session.commit()
    return {"message": "密码修改成功"}


@router.delete("/me")
async def delete_my_account(
    delete_request: UserDeleteRequest, current_user: CurrentUser, session: SessionDep
):
    """注销当前用户账户(需要验证密码)"""
    # 验证密码
    if not verify_password(delete_request.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码错误")

    await session.delete(current_user)
    await session.commit()
    return {"message": "账户已注销"}


# ============ 管理员功能 ============
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: AdminUserCreate, session: SessionDep, current_admin: CurrentAdmin
):
    """管理员创建用户"""
    # 检查用户名是否已存在
    statement = select(User).where(User.username == user_create.username)
    existing_user = (await session.execute(statement)).scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    statement = select(User).where(User.email == user_create.email)
    existing_email = (await session.execute(statement)).scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    # 检查手机号是否已存在
    if user_create.phone:
        statement = select(User).where(User.phone == user_create.phone)
        existing_phone = (await session.execute(statement)).scalars().first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="手机号已被注册"
            )

    # 创建新用户
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        phone=user_create.phone,
        hashed_password=hashed_password,
        user_type=user_create.user_type,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get("/", response_model=PageResponse[UserResponse])
async def list_users(
    session: SessionDep,
    current_admin: CurrentAdmin,
    skip: int = 0,
    limit: int = 100,
    user_type: str | None = None,
    search: str | None = None,
):
    """管理员查询用户列表"""
    from sqlalchemy import func, or_

    # 构建基础查询
    statement = select(User)
    count_statement = select(func.count()).select_from(User)

    # 按用户类型筛选
    if user_type:
        statement = statement.where(User.user_type == user_type)
        count_statement = count_statement.where(User.user_type == user_type)

    # 按关键词搜索（用户名、邮箱、手机号）
    if search:
        search_condition = or_(
            User.username.like(f"%{search}%"),  # type: ignore
            User.email.like(f"%{search}%"),  # type: ignore
            User.phone.like(f"%{search}%") if User.phone else False,  # type: ignore
        )
        statement = statement.where(search_condition)
        count_statement = count_statement.where(search_condition)

    # 获取总数
    total = (await session.execute(count_statement)).scalar_one()

    # 分页查询
    statement = statement.offset(skip).limit(limit)
    users = list((await session.execute(statement)).scalars().all())

    # 计算当前页码
    current = (skip // limit) + 1 if limit > 0 else 1

    return PageResponse(records=users, total=total, current=current, size=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: SessionDep, current_admin: CurrentAdmin):
    """管理员查询指定用户信息"""
    user = await session.get(User, user_id)
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
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != user.email:
        statement = select(User).where(
            User.email == user_update.email, User.id != user_id
        )
        existing_email = (await session.execute(statement)).scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用"
            )

    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: SessionDep, current_admin: CurrentAdmin):
    """管理员删除指定用户"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    await session.delete(user)
    await session.commit()
    return {"message": "用户已删除"}


@router.post("/batch-delete", response_model=BatchDeleteResponse)
async def batch_delete_users(
    batch_request: BatchDeleteRequest, session: SessionDep, current_admin: CurrentAdmin
):
    """管理员批量删除用户"""
    success_count = 0
    failed_count = 0
    failed_ids = []

    for user_id in batch_request.ids:
        try:
            user = await session.get(User, user_id)
            if user:
                # 防止删除管理员自己
                if user.id == current_admin.id:
                    failed_count += 1
                    failed_ids.append(user_id)
                    continue

                await session.delete(user)
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(user_id)
        except Exception:
            failed_count += 1
            failed_ids.append(user_id)
            # 如果发生错误，回滚当前事务
            await session.rollback()

    # 提交所有成功的删除操作
    if success_count > 0:
        await session.commit()

    return BatchDeleteResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"成功删除 {success_count} 个用户，失败 {failed_count} 个",
    )


@router.put("/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: int,
    session: SessionDep,
    current_admin: CurrentAdmin,
    new_password: str = "123456",
):
    """管理员重置指定用户密码"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 更新密码为默认密码或指定密码
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    await session.commit()
    return {"message": f"密码已重置为: {new_password}"}


@router.post("/reset-password")
async def reset_password(reset_data: UserPasswordReset, session: SessionDep):
    """找回密码（需要验证码）"""
    # 查找用户
    statement = select(User).where(User.email == reset_data.email)
    user = (await session.execute(statement)).scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # TODO: 这里应该验证 verification_code 是否正确
    # 目前简化处理，实际应该有验证码发送和验证逻辑

    # 更新密码
    user.hashed_password = get_password_hash(reset_data.new_password)
    session.add(user)
    await session.commit()
    return {"message": "密码重置成功"}
