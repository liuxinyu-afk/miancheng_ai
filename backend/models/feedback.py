"""问题反馈模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from database import Base

if TYPE_CHECKING:
    from models.user import User


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="反馈用户ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="问题标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="问题描述")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="其他", comment="问题分类: bug/suggestion/account/other")
    contact: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="联系方式(选填)")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", comment="pending=待处理 processing=处理中 resolved=已解决 closed=已关闭")
    reply: Mapped[str | None] = mapped_column(Text, nullable=True, comment="管理员回复")
    reply_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True, comment="回复管理员ID")
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="回复时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="feedbacks")
    admin: Mapped["User | None"] = relationship("User", foreign_keys=[reply_by])
