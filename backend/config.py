"""
绵城AI学习集市 - 全局配置
从 .env 文件读取环境变量，统一管理数据库、JWT、AI接口等配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 应用信息
    APP_NAME: str = "绵城AI学习集市"
    APP_VERSION: str = "2.4.0"
    DEBUG: bool = True

    # MySQL 数据库
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "personal_growth_platform"

    # JWT 鉴权
    SECRET_KEY: str = "dev-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI 大模型接口
    AI_API_URL: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "doubao-pro-32k"
    AI_VISION_MODEL: str = ""  # 视觉模型(支持图片识别)，留空则回退到 AI_MODEL

    @property
    def DATABASE_URL(self) -> str:
        """构建 SQLAlchemy 数据库连接字符串"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
