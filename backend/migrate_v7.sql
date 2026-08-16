-- ================================================================
-- 迁移脚本 V7：自习室大改造
-- 不删除任何已有数据！只做 ALTER TABLE ADD COLUMN 和 CREATE TABLE
-- ================================================================

-- ====== 1. study_room 表新增字段 ======
ALTER TABLE `study_room` 
ADD COLUMN IF NOT EXISTS `tags` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '房间标签，逗号分隔',
ADD COLUMN IF NOT EXISTS `description` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '房间简介',
ADD COLUMN IF NOT EXISTS `announcement` TEXT NOT NULL DEFAULT '' COMMENT '房间公告',
ADD COLUMN IF NOT EXISTS `category` VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '房间分类',
ADD COLUMN IF NOT EXISTS `daily_target_minutes` INT NOT NULL DEFAULT 0 COMMENT '每日目标时长(分钟)';

-- ====== 2. study_room_member 表新增字段 ======
ALTER TABLE `study_room_member`
ADD COLUMN IF NOT EXISTS `today_minutes` INT NOT NULL DEFAULT 0 COMMENT '今日学习时长(分钟)',
ADD COLUMN IF NOT EXISTS `last_study_date` DATE NULL COMMENT '最后学习日期';

-- ====== 3. study_room_message 表新增 zone 字段 ======
ALTER TABLE `study_room_message`
ADD COLUMN IF NOT EXISTS `zone` VARCHAR(20) NOT NULL DEFAULT 'chat' COMMENT '消息分区: chat=闲聊 study=自习';

-- ====== 4. 创建打卡记录表 ======
CREATE TABLE IF NOT EXISTS `study_room_checkin` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '打卡ID',
    `room_id` BIGINT NOT NULL COMMENT '房间ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `completed` TEXT NOT NULL DEFAULT '' COMMENT '今日完成',
    `incomplete` TEXT NOT NULL DEFAULT '' COMMENT '未完成',
    `tomorrow_plan` TEXT NOT NULL DEFAULT '' COMMENT '明日计划',
    `mood` TEXT NOT NULL DEFAULT '' COMMENT '心态碎碎念(选填)',
    `study_minutes` INT NOT NULL DEFAULT 0 COMMENT '本次打卡学习时长(分钟)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '打卡时间',
    INDEX `idx_room_id` (`room_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自习房间结构化打卡记录';

-- ====== 5. 确保之前的迁移已执行 ======
-- 修复 message 表枚举（如果V6还没执行过）
ALTER TABLE `message` 
MODIFY COLUMN `msg_type` ENUM('audit','system','comment','like','friend_request','friend_accept') NOT NULL DEFAULT 'system';

-- 确保审核员名称正确
UPDATE `user` SET `nickname` = '审核员01' WHERE `username` = 'auditor01' AND `nickname` = '审核员张三';
UPDATE `user` SET `nickname` = '审核员02' WHERE `username` = 'auditor02' AND `nickname` = '审核员李四';
UPDATE `user` SET `nickname` = '审核员03' WHERE `username` = 'auditor03' AND `nickname` = '审核员王五';

-- ====== 6. 验证 ======
SELECT 'V7迁移完成！' AS message;
SELECT id, name, tags, description, category, daily_target_minutes FROM `study_room` LIMIT 5;
SELECT id, room_id, user_id, today_minutes, last_study_date FROM `study_room_member` LIMIT 5;
SELECT id, room_id, sender_id, zone FROM `study_room_message` LIMIT 5;
