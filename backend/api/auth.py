"""
认证管理路由
提供用户注册、登录、个人信息管理、教师实名认证等接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.common import ResponseOK, TokenResponse
from schemas.user import (
    UserRegister,
    UserLogin,
    TeacherCertRequest,
    UserUpdate,
    UserOut,
    ChangePasswordRequest,
)
from utils.security import hash_password, verify_password, create_access_token
from utils.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证管理"])


@router.post("/register", response_model=ResponseOK, summary="用户注册")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """用户注册（仅支持 student / teacher 角色），密码使用 bcrypt 加密存储"""
    # 校验角色合法性
    if payload.role not in ("student", "teacher"):
        raise HTTPException(status_code=400, detail="注册角色仅支持 student 或 teacher")

    # 校验账号唯一性
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="该登录账号已被注册")

    # 按角色校验必填字段
    if payload.role == "student":
        if not payload.student_no or not payload.student_no.strip():
            raise HTTPException(status_code=400, detail="学生注册必须提供学号")
    elif payload.role == "teacher":
        if not payload.teacher_no or not payload.teacher_no.strip():
            raise HTTPException(status_code=400, detail="教师注册必须提供教职工号")
        if not payload.cert_image or not payload.cert_image.strip():
            raise HTTPException(status_code=400, detail="教师注册必须上传教师资格证或就职证明")

    if not payload.cert_image or not payload.cert_image.strip():
        raise HTTPException(status_code=400, detail="请上传资格证明图片")

    # 创建用户，密码加密
    # 教师注册后认证状态为 pending（需审核通过后才能发布资料）
    # 学生注册后认证状态为 none（不需要审核）
    cert_status = "pending" if payload.role == "teacher" else "none"

    user = User(
        username=payload.username,
        password=hash_password(payload.password),
        nickname=payload.nickname,
        role=payload.role,
        real_name=payload.real_name,
        student_no=payload.student_no if payload.role == "student" else None,
        teacher_no=payload.teacher_no if payload.role == "teacher" else None,
        cert_image=payload.cert_image,
        cert_status=cert_status,
        status=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    msg = "注册成功" if payload.role == "student" else "注册成功，教师身份待审核通过后可发布资料"
    return ResponseOK(message=msg, data=UserOut.model_validate(user).model_dump())


@router.post("/login", response_model=TokenResponse, summary="用户登录")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """用户登录，校验密码后签发 JWT 令牌，返回 TokenResponse"""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if user.status == 0:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")

    # 生成 JWT，载荷中携带用户角色
    token = create_access_token(subject=user.id, extra_data={"role": user.role})

    # 组装 user 字典（含 id, username, role, nickname, avatar, cert_status）
    user_info = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "cert_status": user.cert_status,
    }
    return TokenResponse(access_token=token, user=user_info)


@router.get("/me", response_model=ResponseOK, summary="获取当前登录用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    return ResponseOK(data=UserOut.model_validate(current_user).model_dump())


@router.put("/me", response_model=ResponseOK, summary="更新个人资料")
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人资料（昵称、头像），仅更新提交的字段"""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)

    return ResponseOK(data=UserOut.model_validate(current_user).model_dump())


@router.post("/change-password", response_model=ResponseOK, summary="修改密码")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码，需验证原密码"""
    if not verify_password(payload.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="原密码不正确")
    if payload.old_password == payload.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与原密码相同")
    current_user.password = hash_password(payload.new_password)
    db.commit()
    return ResponseOK(message="密码修改成功")


@router.post("/teacher-cert", response_model=ResponseOK, summary="教师实名认证申请")
def teacher_cert(
    payload: TeacherCertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """教师实名认证申请，更新真实姓名、教职工号并将认证状态置为 pending"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师角色可申请实名认证")

    current_user.real_name = payload.real_name
    current_user.teacher_no = payload.teacher_no
    current_user.cert_status = "pending"
    db.commit()
    db.refresh(current_user)

    return ResponseOK(data=UserOut.model_validate(current_user).model_dump())
