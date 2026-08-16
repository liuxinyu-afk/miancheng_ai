-- ================================================================
-- 迁移脚本：创建自习房间群聊消息表
-- 执行方式：在 Navicat 或 MySQL 命令行中执行此脚本
-- ================================================================

-- 学习房间群聊消息表
CREATE TABLE IF NOT EXISTS study_room_message (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    room_id BIGINT NOT NULL COMMENT '房间ID',
    sender_id BIGINT NOT NULL COMMENT '发送者用户ID',
    content TEXT NOT NULL COMMENT '消息内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    INDEX idx_room_id (room_id),
    INDEX idx_sender_id (sender_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自习房间群聊消息';

-- 验证表创建成功
SELECT 'study_room_message 表创建成功' AS message;
