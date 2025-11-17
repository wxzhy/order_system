from datetime import datetime, timedelta, timezone
from typing import Any
import hashlib

import jwt
# from passlib.context import CryptContext

# 临时使用简单的 SHA256 加密（无盐），仅用于测试
# ⚠️ 生产环境请使用 passlib 的 bcrypt 或 argon2
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "your-secret-key"  # 请换成环境变量或配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 - 临时使用 SHA256"""
    plain_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return plain_hash == hashed_password


def get_password_hash(password: str) -> str:
    """生成密码哈希 - 临时使用 SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_refesh_token(
    subject: str | Any, expires_delta: timedelta = timedelta(days=7)
) -> str:
    """
    生成刷新令牌，默认过期时间为7天
    该令牌用于获取新的访问令牌
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
