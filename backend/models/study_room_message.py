"""自习房间群聊消息模型"""
from datetime import datetime
from sqlalchemy import BigInteger, Text, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class StudyRoomMessage(Base):
    __tablename__ = "study_room_message"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("study_room.id"), nullable=False, comment="房间ID")
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="发送者ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    # V7 新增：消息分区 chat=闲聊区 study=自习区(打卡记录)
    zone: Mapped[str] = mapped_column(String(20), nullable=False, default="chat", comment="消息分区: chat=闲聊 study=自习")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
