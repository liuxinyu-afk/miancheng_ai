"""学习计划模型（学生专属）"""
from datetime import date, datetime
from sqlalchemy import BigInteger, String, Integer, Enum, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class StudyPlan(Base):
    __tablename__ = "study_plan"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="计划标题")
    subject: Mapped[str] = mapped_column(String(50), nullable=False, default="", comment="学科")
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=120, comment="每日目标时长")
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开始日期")
    end_date: Mapped[date] = mapped_column(Date, nullable=False, comment="结束日期")
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", "abandoned"), nullable=False, default="active", comment="计划状态"
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="进度0-100")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
