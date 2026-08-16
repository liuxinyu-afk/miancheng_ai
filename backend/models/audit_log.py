"""审核记录表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    auditor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="审核员ID")
    content_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="被审核内容ID")
    content_type: Mapped[str] = mapped_column(
        Enum("resource", "achievement", "task_package"), nullable=False, comment="内容类型"
    )
    action: Mapped[str] = mapped_column(
        Enum("approve", "reject"), nullable=False, comment="审核操作"
    )
    reject_reason: Mapped[str | None] = mapped_column(String(500), default=None, comment="驳回理由")
    audit_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="审核时间")
