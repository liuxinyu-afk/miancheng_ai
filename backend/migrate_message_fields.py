"""
数据库迁移脚本：为 message 表添加 related_id 和 sender_id 字段
运行方式: python migrate_message_fields.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def migrate():
    """为 message 表添加 related_id 和 sender_id 字段"""
    with engine.connect() as conn:
        # 检查 related_id 是否已存在
        result = conn.execute(text("SHOW COLUMNS FROM message LIKE 'related_id'"))
        if result.fetchone():
            print("related_id 字段已存在，跳过")
        else:
            conn.execute(text("ALTER TABLE message ADD COLUMN related_id BIGINT NULL COMMENT '关联帖子ID'"))
            print("已添加 related_id 字段")

        # 检查 sender_id 是否已存在
        result = conn.execute(text("SHOW COLUMNS FROM message LIKE 'sender_id'"))
        if result.fetchone():
            print("sender_id 字段已存在，跳过")
        else:
            conn.execute(text("ALTER TABLE message ADD COLUMN sender_id BIGINT NULL COMMENT '发送者用户ID'"))
            print("已添加 sender_id 字段")

        conn.commit()
        print("迁移完成！")

if __name__ == "__main__":
    migrate()
