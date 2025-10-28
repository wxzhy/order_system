from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from sqlmodel import select

from backend.dependencies import SessionDep, CurrentUser
from backend.models import User
from backend.schemas import Token, LoginRequest, UserCreate, UserResponse, TokenRefresh
from backend.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refesh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
import jwt
from backend.security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_create: UserCreate, session: SessionDep):
    """用户注册"""
    # 检查用户名是否已存在
    statement = select(User).where(User.username == user_create.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    statement = select(User).where(User.email == user_create.email)
    existing_email = session.exec(statement).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    # 检查手机号是否已存在
    if user_create.phone:
        statement = select(User).where(User.phone == user_create.phone)
        existing_phone = session.exec(statement).first()
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
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, session: SessionDep):
    """用户登录"""
    # 尝试通过用户名、邮箱或手机号查找用户
    statement = select(User).where(
        (User.username == login_data.username)
        | (User.email == login_data.username)
        | (User.phone == login_data.username)
    )
    user = session.exec(statement).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌和刷新令牌
    access_token = create_access_token(
        subject=user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refesh_token(subject=user.id)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/login/token", response_model=Token)
async def login_oauth(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    """OAuth2 密码模式登录（兼容 Swagger UI）"""
    # 尝试通过用户名、邮箱或手机号查找用户
    statement = select(User).where(
        (User.username == form_data.username)
        | (User.email == form_data.username)
        | (User.phone == form_data.username)
    )
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌和刷新令牌
    access_token = create_access_token(
        subject=user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refesh_token(subject=user.id)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, session: SessionDep):
    """刷新访问令牌"""
    try:
        payload = jwt.decode(
            token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
            )

        # 验证用户是否存在
        user = session.get(User, int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
            )

        # 创建新的访问令牌和刷新令牌
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        new_refresh_token = create_refesh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """获取当前登录用户信息"""
    return current_user
