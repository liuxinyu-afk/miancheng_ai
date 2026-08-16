-- ================================================================
-- 迁移脚本 V8：功能增强
-- #1 角色权限边界 #2 教师学生差异化 #4 资源评分/举报
-- #5 成果标签/匿名 #7 仪表盘趋势 #8 勋章体系
-- 不删除任何已有数据！
-- ================================================================

-- ====== 1. 成果帖子新增字段（标签+匿名发布）======
ALTER TABLE `achievement_post`
ADD COLUMN IF NOT EXISTS `tags` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '内容标签，逗号分隔',
ADD COLUMN IF NOT EXISTS `is_anonymous` INT NOT NULL DEFAULT 0 COMMENT '0=实名 1=匿名';

-- ====== 2. 资源评分表 ======
CREATE TABLE IF NOT EXISTS `resource_rating` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `resource_id` BIGINT NOT NULL COMMENT '资源ID',
    `user_id` BIGINT NOT NULL COMMENT '评分人ID',
    `score` INT NOT NULL DEFAULT 5 COMMENT '评分1-5',
    `comment` VARCHAR(500) DEFAULT '' COMMENT '评价内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_resource_user` (`resource_id`, `user_id`),
    INDEX `idx_resource_id` (`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源评分';

-- ====== 3. 资源举报表 ======
CREATE TABLE IF NOT EXISTS `resource_report` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `resource_id` BIGINT NOT NULL COMMENT '被举报资源ID',
    `reporter_id` BIGINT NOT NULL COMMENT '举报人ID',
    `reason` VARCHAR(50) NOT NULL COMMENT '举报原因',
    `description` TEXT COMMENT '详细描述',
    `status` ENUM('pending','resolved','dismissed') NOT NULL DEFAULT 'pending' COMMENT '处理状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_resource_id` (`resource_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源举报';

-- ====== 4. 勋章定义表 ======
CREATE TABLE IF NOT EXISTS `badge` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL COMMENT '勋章名称',
    `description` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '勋章描述',
    `icon` VARCHAR(50) NOT NULL DEFAULT '🏆' COMMENT '勋章图标(emoji)',
    `category` VARCHAR(30) NOT NULL DEFAULT 'study' COMMENT '勋章分类: study/social/contribution/special',
    `condition_type` VARCHAR(50) NOT NULL COMMENT '触发条件类型',
    `condition_value` INT NOT NULL DEFAULT 0 COMMENT '触发条件值',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='勋章定义';

-- ====== 5. 用户勋章表 ======
CREATE TABLE IF NOT EXISTS `user_badge` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `badge_id` BIGINT NOT NULL COMMENT '勋章ID',
    `awarded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_badge` (`user_id`, `badge_id`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户勋章';

-- ====== 6. 学习计划表（学生专属）======
CREATE TABLE IF NOT EXISTS `study_plan` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `title` VARCHAR(100) NOT NULL COMMENT '计划标题',
    `subject` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '学科',
    `daily_goal_minutes` INT NOT NULL DEFAULT 120 COMMENT '每日目标时长(分钟)',
    `start_date` DATE NOT NULL COMMENT '开始日期',
    `end_date` DATE NOT NULL COMMENT '结束日期',
    `status` ENUM('active','completed','abandoned') NOT NULL DEFAULT 'active' COMMENT '计划状态',
    `progress` INT NOT NULL DEFAULT 0 COMMENT '进度0-100',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习计划(学生专属)';

-- ====== 7. 插入勋章初始数据 ======
INSERT INTO `badge` (`name`, `description`, `icon`, `category`, `condition_type`, `condition_value`) VALUES
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
('坚持不懈', '注册满30天', '🌳', 'special', 'register_days', 30)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- ====== 8. 确保之前的迁移已执行 ======
-- V7的study_room字段
ALTER TABLE `study_room`
ADD COLUMN IF NOT EXISTS `tags` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '房间标签',
ADD COLUMN IF NOT EXISTS `description` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '房间简介',
ADD COLUMN IF NOT EXISTS `announcement` TEXT NOT NULL DEFAULT '' COMMENT '房间公告',
ADD COLUMN IF NOT EXISTS `category` VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '房间分类',
ADD COLUMN IF NOT EXISTS `daily_target_minutes` INT NOT NULL DEFAULT 0 COMMENT '每日目标时长';

-- V7的member字段
ALTER TABLE `study_room_member`
ADD COLUMN IF NOT EXISTS `today_minutes` INT NOT NULL DEFAULT 0 COMMENT '今日学习时长',
ADD COLUMN IF NOT EXISTS `last_study_date` DATE NULL COMMENT '最后学习日期';

-- V7的message zone字段
ALTER TABLE `study_room_message`
ADD COLUMN IF NOT EXISTS `zone` VARCHAR(20) NOT NULL DEFAULT 'chat' COMMENT '消息分区';

-- V7的打卡表
CREATE TABLE IF NOT EXISTS `study_room_checkin` (
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
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- message表枚举修复
ALTER TABLE `message`
MODIFY COLUMN `msg_type` ENUM('audit','system','comment','like','friend_request','friend_accept') NOT NULL DEFAULT 'system';

-- 审核员名称修正
UPDATE `user` SET `nickname` = '审核员01' WHERE `username` = 'auditor01' AND (`nickname` = '审核员张三' OR `nickname` = '');
UPDATE `user` SET `nickname` = '审核员02' WHERE `username` = 'auditor02' AND (`nickname` = '审核员李四' OR `nickname` = '');
UPDATE `user` SET `nickname` = '审核员03' WHERE `username` = 'auditor03' AND (`nickname` = '审核员王五' OR `nickname` = '');

-- ====== 验证 ======
SELECT 'V8迁移完成！' AS message;
SELECT id, name, icon, category FROM `badge`;
