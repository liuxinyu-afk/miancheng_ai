-- ================================================================
-- 数据库修复脚本
-- 修复 message 表的 msg_type 枚举值
-- 如果你的 init.sql 执行后仍然出现 friend_request 枚举错误，
-- 请在 Navicat 中执行此脚本
-- ================================================================

USE personal_growth_platform;

-- 修复 message 表的 msg_type 枚举，添加 friend_request 和 friend_accept
ALTER TABLE `message`
    MODIFY COLUMN `msg_type`
    ENUM('audit','system','comment','like','friend_request','friend_accept')
    NOT NULL DEFAULT 'system'
    COMMENT '消息类型';

-- 确认修改成功
SELECT COLUMN_TYPE, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'personal_growth_platform'
  AND TABLE_NAME = 'message'
  AND COLUMN_NAME = 'msg_type';
