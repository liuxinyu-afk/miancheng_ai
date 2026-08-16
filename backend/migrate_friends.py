"""
数据库迁移脚本：
1. 创建 friendship 表
2. 更新 message 表的 msg_type 枚举（添加 friend_request / friend_accept）

运行方式: python migrate_friends.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text


def migrate():
    with engine.connect() as conn:
        # ========== 1. 创建 friendship 表 ==========
        print("=== 检查 friendship 表 ===")

        result = conn.execute(text("SHOW TABLES LIKE 'friendship'"))
        if result.fetchone():
            print("  friendship 表已存在，跳过")
        else:
            conn.execute(text("""
                CREATE TABLE friendship (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    requester_id BIGINT NOT NULL COMMENT '发起者ID',
                    receiver_id BIGINT NOT NULL COMMENT '接收者ID',
                    status ENUM('pending','accepted','rejected') NOT NULL DEFAULT 'pending' COMMENT '好友状态',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_friendship_pair (requester_id, receiver_id),
                    CONSTRAINT fk_fs_req FOREIGN KEY (requester_id) REFERENCES user(id),
                    CONSTRAINT fk_fs_rec FOREIGN KEY (receiver_id) REFERENCES user(id),
                    INDEX idx_fs_receiver (receiver_id, status),
                    INDEX idx_fs_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='好友关系表'
            """))
            print("  ✓ 已创建 friendship 表")

        # ========== 2. 更新 message 表 msg_type 枚举 ==========
        print("=== 检查 message 表 msg_type 枚举 ===")

        result = conn.execute(text("SHOW COLUMNS FROM message LIKE 'msg_type'"))
        col = result.fetchone()
        if col:
            current_type = str(col[1])
            if "friend_request" in current_type:
                print("  msg_type 已包含 friend_request，跳过")
            else:
                conn.execute(text("""
                    ALTER TABLE message
                    MODIFY COLUMN msg_type ENUM('audit','system','comment','like','friend_request','friend_accept')
                    NOT NULL DEFAULT 'system' COMMENT '消息类型'
                """))
                print("  ✓ 已更新 msg_type 枚举（添加 friend_request / friend_accept）")

        conn.commit()
        print("\n迁移完成！")


if __name__ == "__main__":
    migrate()
