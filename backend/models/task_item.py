"""子任务表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from database import Base

if TYPE_CHECKING:
    from models.task_package import TaskPackage


class TaskItem(Base):
    __tablename__ = "task_item"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_package.id"), nullable=False, comment="所属任务包ID")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="任务名称")
    description: Mapped[str | None] = mapped_column(Text, default=None, comment="任务描述")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="任务排序")
    estimated_hours: Mapped[float] = mapped_column(Numeric(5, 1), default=1.0, comment="预计学习时长")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关联任务包
    package: Mapped["TaskPackage"] = relationship("TaskPackage", back_populates="items")
