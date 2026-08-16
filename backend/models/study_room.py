"""结伴自习房间 & 成员表模型"""
from datetime import datetime, date
from sqlalchemy import BigInteger, String, Integer, Enum, DateTime, Date, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class StudyRoom(Base):
    __tablename__ = "study_room"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="房间名称")
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="创建者ID")
    target_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=120, comment="目标自习时长(分钟)")
    is_private: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="0=公开 1=私密")
    max_members: Mapped[int] = mapped_column(Integer, nullable=False, default=10, comment="最大成员数")
    status: Mapped[str] = mapped_column(
        Enum("active", "ended"), nullable=False, default="active", comment="房间状态"
    )
    # V7 新增字段
    tags: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="房间标签，逗号分隔")
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="", comment="房间简介")
    announcement: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="房间公告")
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="其他", comment="房间分类: 考研/编程/英语考试/职业发展/其他"
    )
    daily_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="每日目标时长(分钟), 0=不限")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class StudyRoomMember(Base):
    __tablename__ = "study_room_member"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("study_room.id"), nullable=False, comment="房间ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    study_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="累计自习时长(分钟)")
    is_studying: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="是否正在自习")
    # V7 新增字段
    today_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="今日学习时长(分钟)")
    last_study_date: Mapped[date] = mapped_column(Date, nullable=True, comment="最后学习日期,用于每日重置")
    # V8 新增字段：成员状态审核机制
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", comment="成员状态: active=正常 pending=待审核 kicked=被踢出"
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class StudyRoomCheckin(Base):
    """结构化打卡记录"""
    __tablename__ = "study_room_checkin"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("study_room.id"), nullable=False, comment="房间ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    completed: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="今日完成")
    incomplete: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="未完成")
    tomorrow_plan: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="明日计划")
    mood: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="心态碎碎念(选填)")
    study_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="本次打卡学习时长(分钟)")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
