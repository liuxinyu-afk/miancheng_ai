"""好友关系模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Enum, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Friendship(Base):
    """好友关系表"""
    __tablename__ = "friendship"
    __table_args__ = (
        UniqueConstraint("requester_id", "receiver_id", name="uq_friendship_pair"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    requester_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="发起者ID")
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="接收者ID")
    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "rejected"), nullable=False, default="pending", comment="好友状态"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
