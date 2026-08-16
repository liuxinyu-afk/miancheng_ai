"""资源集市表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class MarketResource(Base):
    __tablename__ = "market_resource"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="资源标题")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="其他", comment="资源分类")
    content: Mapped[str | None] = mapped_column(Text, default=None, comment="资源内容")
    attachment_url: Mapped[str | None] = mapped_column(String(500), default=None, comment="附件地址")
    publisher_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="发布人ID")
    publisher_role: Mapped[str] = mapped_column(
        Enum("student", "teacher"), nullable=False, default="student", comment="发布人身份"
    )
    is_teacher_certified: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="教师认证标识")
    audit_status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected"), nullable=False, default="pending", comment="审核状态"
    )
    reject_reason: Mapped[str | None] = mapped_column(String(500), default=None, comment="驳回理由")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="浏览次数")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
