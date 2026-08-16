"""
安全工具：密码加密 & JWT 令牌生成/验证
使用 bcrypt 库直接进行密码哈希（兼容 bcrypt 4.x+）
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError

from config import settings


def hash_password(password: str) -> str:
    """明文密码 -> bcrypt 哈希"""
    # bcrypt 限制密码最大 72 字节，截断处理
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配"""
    try:
        password_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, extra_data: dict[str, Any] | None = None) -> str:
    """
    生成 JWT access token
    :param subject: 用户ID（字符串或整数）
    :param extra_data: 额外载荷数据（如角色）
    :return: JWT 字符串
    """
    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra_data:
        to_encode.update(extra_data)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    解析 JWT token，返回载荷字典；失败返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
