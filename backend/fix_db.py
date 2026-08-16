"""
数据库修复脚本 - 添加缺失的列
运行方式: python fix_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text, inspect

def fix_database():
    inspector = inspect(engine)

    # ============ 1. 修复 achievement_comment 表（缺 parent_id 列） ============
    try:
        comment_cols = {c['name'] for c in inspector.get_columns('achievement_comment')}
        with engine.connect() as conn:
            if 'parent_id' not in comment_cols:
                print("正在添加 achievement_comment.parent_id 列...")
                conn.execute(text("ALTER TABLE `achievement_comment` ADD COLUMN `parent_id` BIGINT NULL"))
                conn.commit()
                print("  parent_id 列添加成功")
            else:
                print("  achievement_comment.parent_id 列已存在，跳过")
    except Exception as e:
        print(f"  achievement_comment 修复出错: {e}")

    # ============ 2. 修复 achievement_post 表（缺 tags / is_anonymous 列） ============
    try:
        post_cols = {c['name'] for c in inspector.get_columns('achievement_post')}
        with engine.connect() as conn:
            if 'tags' not in post_cols:
                print("正在添加 achievement_post.tags 列...")
                conn.execute(text("ALTER TABLE `achievement_post` ADD COLUMN `tags` VARCHAR(255) NOT NULL DEFAULT ''"))
                conn.commit()
                print("  tags 列添加成功")
            else:
                print("  achievement_post.tags 列已存在，跳过")

            if 'is_anonymous' not in post_cols:
                print("正在添加 achievement_post.is_anonymous 列...")
                conn.execute(text("ALTER TABLE `achievement_post` ADD COLUMN `is_anonymous` INT NOT NULL DEFAULT 0"))
                conn.commit()
                print("  is_anonymous 列添加成功")
            else:
                print("  achievement_post.is_anonymous 列已存在，跳过")
    except Exception as e:
        print(f"  achievement_post 修复出错: {e}")

    # ============ 3. 修复 user 表（缺 cert_status / last_login_at / student_no / cert_image 列） ============
    try:
        user_cols = {c['name'] for c in inspector.get_columns('user')}
        with engine.connect() as conn:
            if 'cert_status' not in user_cols:
                print("正在添加 user.cert_status 列...")
                conn.execute(text("ALTER TABLE `user` ADD COLUMN `cert_status` VARCHAR(20) DEFAULT 'none'"))
                conn.commit()
                print("  cert_status 列添加成功")
            else:
                print("  user.cert_status 列已存在，跳过")

            if 'last_login_at' not in user_cols:
                print("正在添加 user.last_login_at 列...")
                conn.execute(text("ALTER TABLE `user` ADD COLUMN `last_login_at` DATETIME NULL"))
                conn.commit()
                print("  last_login_at 列添加成功")
            else:
                print("  user.last_login_at 列已存在，跳过")

            if 'student_no' not in user_cols:
                print("正在添加 user.student_no 列...")
                conn.execute(text("ALTER TABLE `user` ADD COLUMN `student_no` VARCHAR(30) NULL"))
                conn.commit()
                print("  student_no 列添加成功")
            else:
                print("  user.student_no 列已存在，跳过")

            if 'cert_image' not in user_cols:
                print("正在添加 user.cert_image 列...")
                conn.execute(text("ALTER TABLE `user` ADD COLUMN `cert_image` TEXT NULL"))
                conn.commit()
                print("  cert_image 列添加成功")
            else:
                print("  user.cert_image 列已存在，跳过")
    except Exception as e:
        print(f"  user 表修复出错: {e}")

    # ============ 4. 修复 study_room_member 表（添加 status 列） ============
    try:
        member_cols = {c['name'] for c in inspector.get_columns('study_room_member')}
        with engine.connect() as conn:
            if 'status' not in member_cols:
                print("正在添加 study_room_member.status 列...")
                conn.execute(text("ALTER TABLE `study_room_member` ADD COLUMN `status` VARCHAR(20) NOT NULL DEFAULT 'active'"))
                conn.commit()
                print("  status 列添加成功")
                # 将已有成员全部设为 active
                conn.execute(text("UPDATE `study_room_member` SET `status` = 'active' WHERE `status` IS NULL OR `status` = ''"))
                conn.commit()
                print("  已有成员状态已设为 active")
            else:
                print("  study_room_member.status 列已存在，跳过")
    except Exception as e:
        print(f"  study_room_member 修复出错: {e}")

    print("\n数据库修复完成！")


if __name__ == "__main__":
    fix_database()
