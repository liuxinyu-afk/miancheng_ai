-- ================================================================
-- 迁移脚本 V6：修复数据库枚举 + 更新审核员名称
-- 不会删除任何数据！只做 ALTER 和 UPDATE
-- 在 Navicat 中执行此脚本即可
-- ================================================================

-- ====== 1. 修复 message 表的 msg_type 枚举 ======
-- 问题：旧数据库的 msg_type 枚举缺少 friend_request 和 friend_accept
-- 导致后端报错：'friend_request' is not among the defined enum values

ALTER TABLE `message` 
MODIFY COLUMN `msg_type` ENUM('audit','system','comment','like','friend_request','friend_accept') NOT NULL DEFAULT 'system';

-- ====== 2. 更新审核员名称 ======
-- 用户要求：审核员张三 → 审核员01，审核员李四 → 审核员02，审核员王五 → 审核员03
UPDATE `user` SET `nickname` = '审核员01' WHERE `username` = 'auditor01' AND `nickname` = '审核员张三';
UPDATE `user` SET `nickname` = '审核员02' WHERE `username` = 'auditor02' AND `nickname` = '审核员李四';
UPDATE `user` SET `nickname` = '审核员03' WHERE `username` = 'auditor03' AND `nickname` = '审核员王五';

-- ====== 3. 确保 study_room_message 表存在 ======
CREATE TABLE IF NOT EXISTS `study_room_message` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    `room_id` BIGINT NOT NULL COMMENT '房间ID',
    `sender_id` BIGINT NOT NULL COMMENT '发送者用户ID',
    `content` TEXT NOT NULL COMMENT '消息内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    INDEX `idx_room_id` (`room_id`),
    INDEX `idx_sender_id` (`sender_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自习房间群聊消息';

-- ====== 4. 验证 ======
SELECT '迁移完成！' AS message;
SELECT id, username, nickname, role FROM `user` WHERE role = 'auditor';
