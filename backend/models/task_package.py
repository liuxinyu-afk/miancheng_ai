"""任务包表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TaskPackage(Base):
    __tablename__ = "task_package"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="任务标题")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="其他", comment="任务分类")
    source: Mapped[str] = mapped_column(
        Enum("ai_generated", "user_published"),
        nullable=False, default="ai_generated", comment="生成来源"
    )
    publisher_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"), default=None, comment="发布人ID")
    description: Mapped[str | None] = mapped_column(Text, default=None, comment="简介描述")
    daily_hours: Mapped[int] = mapped_column(Integer, default=2, comment="每日学习时长")
    level: Mapped[str] = mapped_column(String(20), default="beginner", comment="基础水平")
    is_official: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="是否官方认证")
    audit_status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected"),
        nullable=False, default="pending", comment="审核状态"
    )
    reject_reason: Mapped[str | None] = mapped_column(String(500), default=None, comment="驳回理由")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联子任务
    items: Mapped[list["TaskItem"]] = relationship(
        "TaskItem", back_populates="package", cascade="all, delete-orphan"
    )


# 避免循环导入，延迟引用
from models.task_item import TaskItem  # noqa: E402
