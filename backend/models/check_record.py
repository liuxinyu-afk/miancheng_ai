"""打卡记录表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CheckRecord(Base):
    __tablename__ = "check_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_item.id"), nullable=False, comment="子任务ID")
    status: Mapped[str] = mapped_column(
        Enum("completed", "incomplete"), nullable=False, default="completed", comment="打卡状态"
    )
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment="学习备注")
    check_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="打卡时间")
