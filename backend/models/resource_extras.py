"""资源评分 & 举报模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, Enum, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ResourceRating(Base):
    __tablename__ = "resource_rating"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    resource_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("market_resource.id"), nullable=False, comment="资源ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="评分人ID")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=5, comment="评分1-5")
    comment: Mapped[str] = mapped_column(String(500), default="", comment="评价内容")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("resource_id", "user_id", name="uk_resource_user"),)


class ResourceReport(Base):
    __tablename__ = "resource_report"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    resource_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("market_resource.id"), nullable=False, comment="被举报资源ID")
    reporter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="举报人ID")
    reason: Mapped[str] = mapped_column(String(50), nullable=False, comment="举报原因")
    description: Mapped[str] = mapped_column(Text, default="", comment="详细描述")
    status: Mapped[str] = mapped_column(
        Enum("pending", "resolved", "dismissed"), nullable=False, default="pending", comment="处理状态"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
