"""
综合数据库修复脚本
补全所有缺失的表和列，适配 TiDB Cloud
在服务器上运行: cd /opt/miancheng_ai/backend && python3 fix_all_tables.py
"""
import pymysql
from config import settings

SSL_CONFIG = {'ssl': {}} if settings.DB_SSL else None

conn = pymysql.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
    charset='utf8mb4',
    ssl=SSL_CONFIG,
)
cur = conn.cursor()

def safe_execute(sql, desc=""):
    try:
        cur.execute(sql)
        conn.commit()
        print(f"[OK] {desc}")
    except Exception as e:
        if "Duplicate column" in str(e) or "already exists" in str(e):
            print(f"[SKIP] {desc} (already exists)")
        else:
            print(f"[WARN] {desc}: {e}")
        conn.commit()

def safe_executes(sql, desc=""):
    try:
        cur.execute(sql)
        conn.commit()
        print(f"[OK] {desc}")
    except Exception as e:
        print(f"[WARN] {desc}: {e}")
        conn.commit()

print("========== 开始修复数据库 ==========")

# ====== 1. user 表补充列 ======
safe_execute("ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `student_no` VARCHAR(30) DEFAULT NULL COMMENT '学号'", "user.student_no")
safe_execute("ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `cert_image` TEXT DEFAULT NULL COMMENT '资格证明图片URL'", "user.cert_image")

# ====== 2. study_room 表补充列 (V7) ======
safe_execute("ALTER TABLE `study_room` ADD COLUMN IF NOT EXISTS `tags` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '房间标签'", "study_room.tags")
safe_execute("ALTER TABLE `study_room` ADD COLUMN IF NOT EXISTS `description` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '房间简介'", "study_room.description")
safe_execute("ALTER TABLE `study_room` ADD COLUMN IF NOT EXISTS `announcement` TEXT NOT NULL DEFAULT '' COMMENT '房间公告'", "study_room.announcement")
safe_execute("ALTER TABLE `study_room` ADD COLUMN IF NOT EXISTS `category` VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '房间分类'", "study_room.category")
safe_execute("ALTER TABLE `study_room` ADD COLUMN IF NOT EXISTS `daily_target_minutes` INT NOT NULL DEFAULT 0 COMMENT '每日目标时长'", "study_room.daily_target_minutes")

# ====== 3. study_room_member 表补充列 (V7) ======
safe_execute("ALTER TABLE `study_room_member` ADD COLUMN IF NOT EXISTS `today_minutes` INT NOT NULL DEFAULT 0 COMMENT '今日学习时长'", "study_room_member.today_minutes")
safe_execute("ALTER TABLE `study_room_member` ADD COLUMN IF NOT EXISTS `last_study_date` DATE NULL COMMENT '最后学习日期'", "study_room_member.last_study_date")

# ====== 4. study_room_message 表补充列 (V7) ======
safe_execute("ALTER TABLE `study_room_message` ADD COLUMN IF NOT EXISTS `zone` VARCHAR(20) NOT NULL DEFAULT 'chat' COMMENT '消息分区'", "study_room_message.zone")

# ====== 5. achievement_post 表补充列 (V8) ======
safe_execute("ALTER TABLE `achievement_post` ADD COLUMN IF NOT EXISTS `tags` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '内容标签'", "achievement_post.tags")
safe_execute("ALTER TABLE `achievement_post` ADD COLUMN IF NOT EXISTS `is_anonymous` INT NOT NULL DEFAULT 0 COMMENT '0=实名 1=匿名'", "achievement_post.is_anonymous")

# ====== 6. message 表枚举修复 ======
safe_execute("ALTER TABLE `message` MODIFY COLUMN `msg_type` ENUM('audit','system','comment','like','friend_request','friend_accept') NOT NULL DEFAULT 'system'", "message.msg_type enum fix")

# ====== 7. 创建 study_room_checkin 表 (V7) ======
safe_executes("""CREATE TABLE IF NOT EXISTS `study_room_checkin` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `room_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL,
    `completed` TEXT NOT NULL DEFAULT '',
    `incomplete` TEXT NOT NULL DEFAULT '',
    `tomorrow_plan` TEXT NOT NULL DEFAULT '',
    `mood` TEXT NOT NULL DEFAULT '',
    `study_minutes` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_room_id` (`room_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自习房间打卡记录'""", "study_room_checkin table")

# ====== 8. 创建 badge 表 (V8) ======
safe_executes("""CREATE TABLE IF NOT EXISTS `badge` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL COMMENT '勋章名称',
    `description` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '勋章描述',
    `icon` VARCHAR(50) NOT NULL DEFAULT '🏆' COMMENT '勋章图标',
    `category` VARCHAR(30) NOT NULL DEFAULT 'study' COMMENT '勋章分类',
    `condition_type` VARCHAR(50) NOT NULL COMMENT '触发条件类型',
    `condition_value` INT NOT NULL DEFAULT 0 COMMENT '触发条件值',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='勋章定义'""", "badge table")

# ====== 9. 创建 user_badge 表 (V8) ======
safe_executes("""CREATE TABLE IF NOT EXISTS `user_badge` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `badge_id` BIGINT NOT NULL COMMENT '勋章ID',
    `awarded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_badge` (`user_id`, `badge_id`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户勋章'""", "user_badge table")

# ====== 10. 创建 study_plan 表 (V8) ======
safe_executes("""CREATE TABLE IF NOT EXISTS `study_plan` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `title` VARCHAR(100) NOT NULL COMMENT '计划标题',
    `subject` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '学科',
    `daily_goal_minutes` INT NOT NULL DEFAULT 120 COMMENT '每日目标时长',
    `start_date` DATE NOT NULL COMMENT '开始日期',
    `end_date` DATE NOT NULL COMMENT '结束日期',
    `status` ENUM('active','completed','abandoned') NOT NULL DEFAULT 'active' COMMENT '计划状态',
    `progress` INT NOT NULL DEFAULT 0 COMMENT '进度0-100',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习计划'""", "study_plan table")

# ====== 11. 创建 resource_rating 表 (V8) ======
safe_executes("""CREATE TABLE IF NOT EXISTS `resource_rating` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `resource_id` BIGINT NOT NULL COMMENT '资源ID',
    `user_id` BIGINT NOT NULL COMMENT '评分人ID',
    `score` INT NOT NULL DEFAULT 5 COMMENT '评分1-5',
    `comment` VARCHAR(500) DEFAULT '' COMMENT '评价内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_resource_user` (`resource_id`, `user_id`),
    INDEX `idx_resource_id` (`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源评分'""", "resource_rating table")

# ====== 12. 创建 resource_report 表 (V8) ======
safe_executes("""CREATE TABLE IF NOT EXISTS `resource_report` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `resource_id` BIGINT NOT NULL COMMENT '被举报资源ID',
    `reporter_id` BIGINT NOT NULL COMMENT '举报人ID',
    `reason` VARCHAR(50) NOT NULL COMMENT '举报原因',
    `description` TEXT COMMENT '详细描述',
    `status` ENUM('pending','resolved','dismissed') NOT NULL DEFAULT 'pending' COMMENT '处理状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_resource_id` (`resource_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源举报'""", "resource_report table")

# ====== 13. 创建 feedback 表 ======
safe_executes("""CREATE TABLE IF NOT EXISTS `feedback` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '反馈用户ID',
    `title` VARCHAR(200) NOT NULL COMMENT '问题标题',
    `content` TEXT NOT NULL COMMENT '问题描述',
    `category` VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '问题分类',
    `contact` VARCHAR(100) DEFAULT NULL COMMENT '联系方式',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '处理状态',
    `reply` TEXT DEFAULT NULL COMMENT '管理员回复',
    `reply_by` BIGINT DEFAULT NULL COMMENT '回复管理员ID',
    `replied_at` DATETIME DEFAULT NULL COMMENT '回复时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问题反馈'""", "feedback table")

# ====== 14. 创建 resource_request 表 ======
safe_executes("""CREATE TABLE IF NOT EXISTS `resource_request` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '请求人ID',
    `title` VARCHAR(200) NOT NULL COMMENT '资源标题',
    `category` VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '资源分类',
    `description` TEXT COMMENT '需求描述',
    `status` ENUM('open','fulfilled','closed') NOT NULL DEFAULT 'open' COMMENT '状态',
    `view_count` INT NOT NULL DEFAULT 0 COMMENT '浏览次数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源请求'""", "resource_request table")

# ====== 15. 插入勋章初始数据 ======
badge_data = [
    ('学习新星', '累计学习满10小时', '⭐', 'study', 'study_minutes', 600),
    ('学习达人', '累计学习满50小时', '🌟', 'study', 'study_minutes', 3000),
    ('学习大师', '累计学习满200小时', '🏆', 'study', 'study_minutes', 12000),
    ('打卡先锋', '累计打卡满7次', '🔥', 'study', 'checkin_count', 7),
    ('打卡狂魔', '累计打卡满30次', '💪', 'study', 'checkin_count', 30),
    ('社交蝴蝶', '添加满5个好友', '🦋', 'social', 'friend_count', 5),
    ('人气王', '收到满10个点赞', '❤️', 'social', 'like_received', 10),
    ('贡献者', '发布满5个资源', '📦', 'contribution', 'resource_count', 5),
    ('知识传播者', '发布满20个资源', '📚', 'contribution', 'resource_count', 20),
    ('成果展示', '发布满3个成果帖子', '🎓', 'contribution', 'post_count', 3),
    ('自习室达人', '创建满3个自习房间', '🏠', 'contribution', 'room_count', 3),
    ('初心不忘', '注册满7天', '🌱', 'special', 'register_days', 7),
    ('坚持不懈', '注册满30天', '🌳', 'special', 'register_days', 30),
]
for name, desc, icon, cat, cond_type, cond_val in badge_data:
    try:
        cur.execute(
            "INSERT IGNORE INTO `badge` (`name`, `description`, `icon`, `category`, `condition_type`, `condition_value`) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, desc, icon, cat, cond_type, cond_val)
        )
    except Exception as e:
        pass
conn.commit()
print(f"[OK] badge seed data ({len(badge_data)} badges)")

# ====== 16. 审核员名称修正 ======
safe_execute("UPDATE `user` SET `nickname` = '审核员01' WHERE `username` = 'auditor01' AND (`nickname` = '审核员张三' OR `nickname` = '')", "fix auditor01 name")
safe_execute("UPDATE `user` SET `nickname` = '审核员02' WHERE `username` = 'auditor02' AND (`nickname` = '审核员李四' OR `nickname` = '')", "fix auditor02 name")
safe_execute("UPDATE `user` SET `nickname` = '审核员03' WHERE `username` = 'auditor03' AND (`nickname` = '审核员王五' OR `nickname` = '')", "fix auditor03 name")

# ====== 验证 ======
print("\n========== 验证表结构 ==========")
cur.execute("SHOW TABLES")
tables = [r[0] for r in cur.fetchall()]
print(f"数据库表 ({len(tables)}): {', '.join(tables)}")

cur.execute("DESCRIBE `user`")
cols = [r[0] for r in cur.fetchall()]
print(f"\nuser 表列: {', '.join(cols)}")

cur.execute("SELECT COUNT(*) FROM `badge`")
badge_count = cur.fetchone()[0]
print(f"\n勋章数量: {badge_count}")

print("\n========== 修复完成！==========")
conn.close()
