"""
FastAPI 依赖注入：JWT 鉴权 & 角色权限校验
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from utils.security import decode_access_token

# Bearer Token 提取器
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    从请求头 Authorization: Bearer <token> 中解析当前登录用户
    未登录或 token 无效返回 401
    """
    if credentials is None or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌，请先登录",
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌无效或已过期，请重新登录",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌载荷异常")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    if user.status == 0:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")

    return user


def require_roles(*roles: str):
    """
    角色权限校验依赖工厂
    用法: @router.get("/...", dependencies=[Depends(require_roles("admin", "auditor"))])
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，当前角色 [{current_user.role}] 无权访问此接口",
            )
        return current_user

    return role_checker


# 常用角色快捷依赖
require_student = require_roles("student", "teacher", "admin")
require_teacher = require_roles("teacher", "admin")
require_auditor = require_roles("auditor", "admin")
require_admin = require_roles("admin")
