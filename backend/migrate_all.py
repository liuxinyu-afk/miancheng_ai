"""
数据库迁移脚本：
1. 为 message 表添加 related_id 和 sender_id 字段
2. 为 achievement_comment 表添加 parent_id 字段
3. 创建 conversation 和 private_message 表

运行方式: python migrate_all.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text


def migrate():
    with engine.connect() as conn:
        # ========== 1. message 表添加字段 ==========
        print("=== 检查 message 表 ===")

        result = conn.execute(text("SHOW COLUMNS FROM message LIKE 'related_id'"))
        if result.fetchone():
            print("  related_id 字段已存在，跳过")
        else:
            conn.execute(text("ALTER TABLE message ADD COLUMN related_id BIGINT NULL COMMENT '关联帖子ID'"))
            print("  ✓ 已添加 related_id 字段")

        result = conn.execute(text("SHOW COLUMNS FROM message LIKE 'sender_id'"))
        if result.fetchone():
            print("  sender_id 字段已存在，跳过")
        else:
            conn.execute(text("ALTER TABLE message ADD COLUMN sender_id BIGINT NULL COMMENT '发送者用户ID'"))
            print("  ✓ 已添加 sender_id 字段")

        # ========== 2. achievement_comment 表添加 parent_id ==========
        print("=== 检查 achievement_comment 表 ===")

        result = conn.execute(text("SHOW COLUMNS FROM achievement_comment LIKE 'parent_id'"))
        if result.fetchone():
            print("  parent_id 字段已存在，跳过")
        else:
            conn.execute(text("ALTER TABLE achievement_comment ADD COLUMN parent_id BIGINT NULL COMMENT '父评论ID（回复用）'"))
            print("  ✓ 已添加 parent_id 字段")

        # ========== 3. 创建私信表 ==========
        print("=== 检查私信表 ===")

        result = conn.execute(text("SHOW TABLES LIKE 'conversation'"))
        if result.fetchone():
            print("  conversation 表已存在，跳过")
        else:
            conn.execute(text("""
                CREATE TABLE conversation (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user1_id BIGINT NOT NULL COMMENT '用户1 ID',
                    user2_id BIGINT NOT NULL COMMENT '用户2 ID',
                    last_message TEXT DEFAULT NULL COMMENT '最后一条消息内容',
                    last_message_at DATETIME DEFAULT NULL COMMENT '最后消息时间',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_conversation_users (user1_id, user2_id),
                    CONSTRAINT fk_conv_user1 FOREIGN KEY (user1_id) REFERENCES user(id),
                    CONSTRAINT fk_conv_user2 FOREIGN KEY (user2_id) REFERENCES user(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='私信会话表'
            """))
            print("  ✓ 已创建 conversation 表")

        result = conn.execute(text("SHOW TABLES LIKE 'private_message'"))
        if result.fetchone():
            print("  private_message 表已存在，跳过")
        else:
            conn.execute(text("""
                CREATE TABLE private_message (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id BIGINT NOT NULL COMMENT '会话ID',
                    sender_id BIGINT NOT NULL COMMENT '发送者ID',
                    receiver_id BIGINT NOT NULL COMMENT '接收者ID',
                    content TEXT NOT NULL COMMENT '消息内容',
                    is_read INT NOT NULL DEFAULT 0 COMMENT '0=未读 1=已读',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_pm_conv FOREIGN KEY (conversation_id) REFERENCES conversation(id),
                    CONSTRAINT fk_pm_sender FOREIGN KEY (sender_id) REFERENCES user(id),
                    CONSTRAINT fk_pm_receiver FOREIGN KEY (receiver_id) REFERENCES user(id),
                    INDEX idx_pm_receiver_read (receiver_id, is_read),
                    INDEX idx_pm_conv (conversation_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='私信消息表'
            """))
            print("  ✓ 已创建 private_message 表")

        conn.commit()
        print("\n迁移完成！")


if __name__ == "__main__":
    migrate()
