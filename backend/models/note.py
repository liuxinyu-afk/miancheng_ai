"""学习笔记表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Note(Base):
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    package_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("task_package.id"), default=None, comment="关联任务包ID")
    title: Mapped[str | None] = mapped_column(String(200), default=None, comment="笔记标题")
    content: Mapped[str | None] = mapped_column(Text, default=None, comment="笔记内容")
    is_public: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="0=私有 1=公开")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
