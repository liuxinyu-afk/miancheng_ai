"""
绵城AI学习集市 - 数据库连接配置
SQLAlchemy 2.0 风格，使用 declarative_base 统一管理所有 ORM 模型
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

# 创建数据库引擎（pool_pre_ping 防止连接断开后报错）
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

# 会话工厂：每个请求创建一个独立 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有模型的基类
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话，请求结束自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
