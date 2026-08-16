"""私信模型：会话表 + 消息表"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Conversation(Base):
    """私信会话表 - 两个用户之间的对话"""
    __tablename__ = "conversation"
    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="uq_conversation_users"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户1 ID")
    user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户2 ID")
    last_message: Mapped[str | None] = mapped_column(Text, default=None, comment="最后一条消息内容")
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment="最后消息时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PrivateMessage(Base):
    """私信消息表"""
    __tablename__ = "private_message"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("conversation.id"), nullable=False, comment="会话ID")
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="发送者ID")
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="接收者ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    is_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="0=未读 1=已读")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
