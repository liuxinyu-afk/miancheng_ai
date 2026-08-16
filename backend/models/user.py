"""用户表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Enum, Integer, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="登录账号")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码(bcrypt)")
    role: Mapped[str] = mapped_column(
        Enum("student", "teacher", "auditor", "admin"),
        nullable=False, default="student", comment="用户角色"
    )
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, comment="昵称")
    avatar: Mapped[str | None] = mapped_column(String(500), default=None, comment="头像URL")
    real_name: Mapped[str | None] = mapped_column(String(50), default=None, comment="真实姓名")
    teacher_no: Mapped[str | None] = mapped_column(String(30), default=None, comment="教职工号")
    student_no: Mapped[str | None] = mapped_column(String(30), default=None, comment="学号")
    cert_image: Mapped[str | None] = mapped_column(Text, default=None, comment="资格证明图片URL（教师资格证/就职证明/学生证）")
    cert_status: Mapped[str] = mapped_column(
        Enum("none", "pending", "approved", "rejected"),
        nullable=False, default="none", comment="实名认证状态"
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="1=启用 0=禁用")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="注册时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
