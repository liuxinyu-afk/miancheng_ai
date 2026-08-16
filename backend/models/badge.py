"""勋章 & 用户勋章模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Badge(Base):
    __tablename__ = "badge"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="勋章名称")
    description: Mapped[str] = mapped_column(String(200), nullable=False, default="", comment="勋章描述")
    icon: Mapped[str] = mapped_column(String(50), nullable=False, default="🏆", comment="勋章图标")
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="study", comment="勋章分类")
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="触发条件类型")
    condition_value: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="触发条件值")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserBadge(Base):
    __tablename__ = "user_badge"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    badge_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("badge.id"), nullable=False, comment="勋章ID")
    awarded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uk_user_badge"),)
