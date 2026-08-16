"""资源收藏 & 消息通知表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Enum, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class UserFavorite(Base):
    __tablename__ = "user_favorite"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    resource_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("market_resource.id"), nullable=False, comment="资源ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="接收用户ID")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="消息标题")
    content: Mapped[str] = mapped_column(String(500), nullable=False, comment="消息内容")
    msg_type: Mapped[str] = mapped_column(
        Enum("audit", "system", "comment", "like", "friend_request", "friend_accept"), nullable=False, default="system", comment="消息类型"
    )
    is_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="0=未读 1=已读")
    # 新增字段：关联帖子ID和发送者ID（评论/点赞通知用）
    related_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="关联帖子ID")
    sender_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="发送者用户ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
