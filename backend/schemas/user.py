"""用户 & 认证相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="登录账号")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    role: str = Field(default="student", description="角色: student/teacher")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    student_no: str | None = Field(None, max_length=30, description="学号（学生必填）")
    teacher_no: str | None = Field(None, max_length=30, description="教职工号（教师必填）")
    cert_image: str = Field(..., min_length=1, description="资格证明图片URL（教师资格证/就职证明/学生证）")


class UserLogin(BaseModel):
    username: str = Field(..., description="登录账号")
    password: str = Field(..., description="密码")


class TeacherCertRequest(BaseModel):
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    teacher_no: str = Field(..., min_length=1, max_length=30, description="教职工号")


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="昵称")
    avatar: str | None = Field(None, max_length=500, description="头像URL")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=100, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    nickname: str
    avatar: str | None = None
    real_name: str | None = None
    teacher_no: str | None = None
    student_no: str | None = None
    cert_image: str | None = None
    cert_status: str = "none"
    status: int = 1
    created_at: datetime

    model_config = {"from_attributes": True}
