from datetime import datetime, timedelta
import hashlib
import random
import string
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, SessionDep
from models import EmailVerificationCode, User, VerificationScene
from schemas import (
    EmailCodeSendRequest,
    EmailLoginRequest,
    LoginRequest,
    Token,
    TokenRefresh,
    UserCreate,
    UserPasswordReset,
    UserPasswordUpdate,
    UserResponse,
    UserUpdate,
)
from security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refesh_token,
    get_password_hash,
    verify_password,
)
from utils.email import send_email

# table ref for typed column access
EmailVerificationTable: Any = getattr(EmailVerificationCode, "__table__", None)

router = APIRouter(prefix="/auth", tags=["认证"])

CODE_LENGTH = 6
CODE_EXPIRE_MINUTES = 10

SCENE_TITLES = {
    VerificationScene.LOGIN: "登录",
    VerificationScene.REGISTER: "注册",
    VerificationScene.RESET_PASSWORD: "重置密码",
}


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _generate_verification_code(length: int = CODE_LENGTH) -> str:
    return "".join(random.choices(string.digits, k=length))


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


async def _store_verification_code(
    session: AsyncSession, email: str, scene: VerificationScene, code: str
) -> EmailVerificationCode:
    await session.execute(
        delete(EmailVerificationCode).where(
            EmailVerificationTable.c.email == email,
            EmailVerificationTable.c.scene == scene,
        )
    )

    verification = EmailVerificationCode(
        email=email,
        scene=scene,
        code_hash=_hash_code(code),
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES),
    )
    session.add(verification)
    await session.commit()
    await session.refresh(verification)
    return verification


def _send_verification_email(email: str, scene: VerificationScene, code: str) -> None:
    action = SCENE_TITLES.get(scene, "操作")
    subject = f"餐饮预订系统{action}验证码"
    body = (
        f"您好！\n\n您正在进行{action}操作，验证码为 {code} ，有效期 {CODE_EXPIRE_MINUTES} 分钟。\n"
        "如非本人操作，请忽略此邮件。"
    )
    send_email(subject, body, email)


async def _verify_email_code(
    session: AsyncSession, email: str, scene: VerificationScene, code: str
) -> None:
    code_hash = _hash_code(code)
    statement = (
        select(EmailVerificationCode)
        .where(
            EmailVerificationTable.c.email == email,
            EmailVerificationTable.c.scene == scene,
            EmailVerificationTable.c.verified == False,
            EmailVerificationTable.c.expires_at >= datetime.utcnow(),
        )
        .order_by(EmailVerificationTable.c.created_at.desc())
    )
    result = await session.execute(statement)
    record = result.scalars().first()
    if not record or record.code_hash != code_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已失效"
        )

    record.verified = True
    session.add(record)
    await session.commit()


def _create_token_response(user: User) -> Token:
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refesh_token(subject=user.id)
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/send-email-code")
async def send_email_code(payload: EmailCodeSendRequest, session: SessionDep):
    email = _normalize_email(payload.email)
    scene = payload.scene

    if scene == VerificationScene.REGISTER:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
            )
    else:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="邮箱尚未注册"
            )

    code = _generate_verification_code()
    verification = await _store_verification_code(session, email, scene, code)

    try:
        _send_verification_email(email, scene, code)
    except RuntimeError as exc:
        await session.delete(verification)
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return {"message": "验证码已发送，请查收邮箱"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_create: UserCreate, session: SessionDep):
    """用户注册"""
    email = _normalize_email(user_create.email)

    statement = select(User).where(User.username == user_create.username)
    result = await session.execute(statement)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    result = await session.execute(select(User).where(User.email == email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    if user_create.phone:
        result = await session.execute(
            select(User).where(User.phone == user_create.phone)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="手机号已被注册"
            )

    await _verify_email_code(
        session, email, VerificationScene.REGISTER, user_create.verification_code
    )

    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=email,
        phone=user_create.phone,
        hashed_password=hashed_password,
        user_type=user_create.user_type,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, session: SessionDep):
    """用户账号密码登录"""
    statement = select(User).where(
        (User.username == login_data.username)
        | (User.email == _normalize_email(login_data.username))
        | (User.phone == login_data.username)
    )
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _create_token_response(user)


@router.post("/login/email", response_model=Token)
async def login_with_email(payload: EmailLoginRequest, session: SessionDep):
    """邮箱验证码登录"""
    email = _normalize_email(payload.email)
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="邮箱尚未注册"
        )
    await _verify_email_code(
        session, email, VerificationScene.LOGIN, payload.verification_code
    )
    return _create_token_response(user)


@router.post("/login/token", response_model=Token)
async def login_oauth(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    """OAuth2 密码模式登录（用于 Swagger UI）"""
    statement = select(User).where(
        (User.username == form_data.username)
        | (User.email == _normalize_email(form_data.username))
        | (User.phone == form_data.username)
    )
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _create_token_response(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, session: SessionDep):
    """刷新访问令牌"""
    try:
        payload = jwt.decode(
            token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
            )

        user = await session.get(User, int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
            )

        return _create_token_response(user)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )


@router.post("/reset-password")
async def reset_password(payload: UserPasswordReset, session: SessionDep):
    """邮箱验证码重置密码"""
    email = _normalize_email(payload.email)
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="邮箱尚未注册"
        )

    await _verify_email_code(
        session, email, VerificationScene.RESET_PASSWORD, payload.verification_code
    )
    user.hashed_password = get_password_hash(payload.new_password)
    session.add(user)
    await session.commit()

    return {"message": "密码已重置，请使用新密码登录"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """获取当前登录用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate, current_user: CurrentUser, session: SessionDep
):
    """更新当前登录用户的个人信息"""
    if user_update.username:
        statement = select(User).where(
            (User.username == user_update.username) & (User.id != current_user.id)
        )
        result = await session.execute(statement)
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被使用"
            )
        current_user.username = user_update.username

    if user_update.email:
        normalized_email = _normalize_email(user_update.email)
        statement = select(User).where(
            (User.email == normalized_email) & (User.id != current_user.id)
        )
        result = await session.execute(statement)
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用"
            )
        current_user.email = normalized_email

    if user_update.phone:
        statement = select(User).where(
            (User.phone == user_update.phone) & (User.id != current_user.id)
        )
        result = await session.execute(statement)
        existing_phone = result.scalars().first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="手机号已被使用"
            )
        current_user.phone = user_update.phone

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.put("/me/password")
async def change_current_user_password(
    password_update: UserPasswordUpdate, current_user: CurrentUser, session: SessionDep
):
    """修改当前登录用户密码"""
    if not verify_password(password_update.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确"
        )

    current_user.hashed_password = get_password_hash(password_update.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "密码修改成功"}
