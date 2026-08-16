"""
绵城AI学习集市 - 数据库连接配置
SQLAlchemy 2.0 风格，使用 declarative_base 统一管理所有 ORM 模型
"""
import ssl

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

# 云数据库（TiDB Cloud / Aiven）需要 SSL 连接
connect_args = {}
if settings.DB_SSL:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx

# 创建数据库引擎
# pool_pre_ping 防止连接断开后报错；免费数据库连接数有限，降低池大小
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_recycle=3600,
    echo=settings.DEBUG,
    connect_args=connect_args,
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