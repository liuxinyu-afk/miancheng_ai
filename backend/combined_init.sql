-- ================================================================
-- 绵城AI学习集市 - 合并数据库初始化脚本
-- 用于云数据库一键导入（TiDB Cloud / Aiven / 其他 MySQL）
-- 执行顺序: init -> seed -> v6 -> v7 -> v8 -> study_room_msg -> fix
-- ================================================================
-- ================================================================
-- 开始执行: init.sql
-- ================================================================

-- ================================================================
-- 个人成长学习平台 —— 数据库初始化脚本
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4 (支持Emoji等4字节字符)
-- 说明: 包含8张核心表 + 6张支撑表 + 种子数据
-- ================================================================
--
-- 【DBeaver 使用说明】
-- 如果用 DBeaver 执行，请按以下步骤操作：
--   1. 先选中下面第1条 CREATE DATABASE 语句，按 Alt+X 单独执行
--   2. 在 DBeaver 左侧右键 personal_growth_platform 数据库 → 激活
--   3. 在 SQL 编辑器顶部的数据库下拉框选择 personal_growth_platform
--   4. 删掉下面 USE 那行，选中剩余全部语句，按 Alt+X 执行
--
-- 【命令行使用说明】
-- mysql -u root -p < init.sql  （一条命令搞定，推荐）
-- ================================================================


-- 第1步：创建数据库（DBeaver用户请单独执行这一条）
CREATE DATABASE IF NOT EXISTS personal_growth_platform
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;


-- 第2步：切换数据库（DBeaver用户请跳过此行，用手动选择数据库代替）
USE personal_growth_platform;


-- 第3步：删除旧表（开发环境用，生产环境请注释掉）
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS private_message;
DROP TABLE IF EXISTS conversation;
DROP TABLE IF EXISTS friendship;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS achievement_comment;
DROP TABLE IF EXISTS achievement_like;
DROP TABLE IF EXISTS achievement_post;
DROP TABLE IF EXISTS study_room_member;
DROP TABLE IF EXISTS study_room;
DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS check_record;
DROP TABLE IF EXISTS market_resource;
DROP TABLE IF EXISTS task_item;
DROP TABLE IF EXISTS task_package;
DROP TABLE IF EXISTS user_favorite;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS user;

SET FOREIGN_KEY_CHECKS = 1;


-- ================================================================
-- 核心表 1: 用户表 (user)
-- 角色: student(学生) / teacher(教师) / auditor(审核员) / admin(管理员)
-- ================================================================
CREATE TABLE `user` (
    `id`                 BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username`           VARCHAR(50)  NOT NULL COMMENT '登录账号',
    `password`           VARCHAR(255) NOT NULL COMMENT '登录密码(bcrypt加密)',
    `role`               ENUM('student','teacher','auditor','admin') NOT NULL DEFAULT 'student' COMMENT '用户角色',
    `nickname`           VARCHAR(50)  NOT NULL COMMENT '昵称',
    `avatar`             VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    `real_name`          VARCHAR(50)  DEFAULT NULL COMMENT '真实姓名(教师认证用)',
    `teacher_no`         VARCHAR(30)  DEFAULT NULL COMMENT '教职工号(教师认证用)',
    `cert_status`        ENUM('none','pending','approved','rejected') NOT NULL DEFAULT 'none' COMMENT '实名认证状态',
    `status`             TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '账号状态: 1=启用 0=禁用',
    `created_at`         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `updated_at`         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- ================================================================
-- 核心表 2: 任务包表 (task_package)
-- 生成来源: ai_generated(AI生成) / user_published(用户发布)
-- ================================================================
CREATE TABLE `task_package` (
    `id`             BIGINT       NOT NULL AUTO_INCREMENT COMMENT '任务包ID',
    `title`          VARCHAR(100) NOT NULL COMMENT '任务标题',
    `category`       VARCHAR(50)  NOT NULL DEFAULT '其他' COMMENT '任务分类: 考研/考证/专业课/技能学习/其他',
    `source`         ENUM('ai_generated','user_published') NOT NULL DEFAULT 'ai_generated' COMMENT '生成来源',
    `publisher_id`   BIGINT       DEFAULT NULL COMMENT '发布人ID(关联user.id)',
    `description`    TEXT         COMMENT '简介描述',
    `daily_hours`    INT          DEFAULT 2 COMMENT '每日学习时长(小时)',
    `level`          VARCHAR(20)  DEFAULT 'beginner' COMMENT '基础水平: beginner/intermediate/advanced',
    `is_official`    TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否官方认证(教师发布)',
    `audit_status`   ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    `reject_reason`  VARCHAR(500) DEFAULT NULL COMMENT '驳回理由',
    `created_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_publisher` (`publisher_id`),
    KEY `idx_category` (`category`),
    KEY `idx_audit_status` (`audit_status`),
    CONSTRAINT `fk_pkg_publisher` FOREIGN KEY (`publisher_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务包表';


-- ================================================================
-- 核心表 3: 子任务表 (task_item)
-- ================================================================
CREATE TABLE `task_item` (
    `id`               BIGINT       NOT NULL AUTO_INCREMENT COMMENT '子任务ID',
    `package_id`       BIGINT       NOT NULL COMMENT '所属任务包ID(关联task_package.id)',
    `name`             VARCHAR(200) NOT NULL COMMENT '任务名称',
    `description`      TEXT         COMMENT '任务描述',
    `sort_order`       INT          NOT NULL DEFAULT 0 COMMENT '任务排序(从小到大)',
    `estimated_hours`  DECIMAL(5,1) DEFAULT 1.0 COMMENT '预计学习时长(小时)',
    `created_at`       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_package` (`package_id`),
    CONSTRAINT `fk_item_package` FOREIGN KEY (`package_id`) REFERENCES `task_package` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='子任务表';


-- ================================================================
-- 核心表 4: 资源集市表 (market_resource)
-- ================================================================
CREATE TABLE `market_resource` (
    `id`                   BIGINT       NOT NULL AUTO_INCREMENT COMMENT '资源ID',
    `title`                VARCHAR(100) NOT NULL COMMENT '资源标题',
    `category`             VARCHAR(50)  NOT NULL DEFAULT '其他' COMMENT '资源分类: 考研/考证/专业课/技能学习/其他',
    `content`              LONGTEXT     COMMENT '资源内容(富文本/Markdown)',
    `attachment_url`       VARCHAR(500) DEFAULT NULL COMMENT '附件地址',
    `publisher_id`         BIGINT       NOT NULL COMMENT '发布人ID(关联user.id)',
    `publisher_role`       ENUM('student','teacher') NOT NULL DEFAULT 'student' COMMENT '发布人身份',
    `is_teacher_certified` TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '教师认证标识',
    `audit_status`         ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    `reject_reason`        VARCHAR(500) DEFAULT NULL COMMENT '驳回理由',
    `view_count`           INT          NOT NULL DEFAULT 0 COMMENT '浏览次数',
    `created_at`           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    `updated_at`           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_publisher` (`publisher_id`),
    KEY `idx_category` (`category`),
    KEY `idx_audit_status` (`audit_status`),
    CONSTRAINT `fk_res_publisher` FOREIGN KEY (`publisher_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资源集市表';


-- ================================================================
-- 核心表 5: 打卡记录表 (check_record)
-- ================================================================
CREATE TABLE `check_record` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '打卡ID',
    `user_id`     BIGINT       NOT NULL COMMENT '用户ID(关联user.id)',
    `task_id`     BIGINT       NOT NULL COMMENT '所属子任务ID(关联task_item.id)',
    `status`      ENUM('completed','incomplete') NOT NULL DEFAULT 'completed' COMMENT '打卡状态',
    `remark`      VARCHAR(500) DEFAULT NULL COMMENT '学习备注',
    `check_time`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '打卡时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_task` (`task_id`),
    KEY `idx_check_time` (`check_time`),
    CONSTRAINT `fk_chk_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_chk_task` FOREIGN KEY (`task_id`) REFERENCES `task_item` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡记录表';


-- ================================================================
-- 核心表 6: 学习笔记表 (note)
-- ================================================================
CREATE TABLE `note` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '笔记ID',
    `user_id`     BIGINT       NOT NULL COMMENT '用户ID(关联user.id)',
    `package_id`  BIGINT       DEFAULT NULL COMMENT '关联任务包ID(关联task_package.id)',
    `title`       VARCHAR(200) DEFAULT NULL COMMENT '笔记标题',
    `content`     LONGTEXT     COMMENT '笔记内容(富文本/Markdown)',
    `is_public`   TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否公开: 0=私有 1=公开',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_package` (`package_id`),
    CONSTRAINT `fk_note_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_note_package` FOREIGN KEY (`package_id`) REFERENCES `task_package` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习笔记表';


-- ================================================================
-- 核心表 7: 成果帖子表 (achievement_post)
-- ================================================================
CREATE TABLE `achievement_post` (
    `id`            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '帖子ID',
    `user_id`       BIGINT       NOT NULL COMMENT '用户ID(关联user.id)',
    `content`       LONGTEXT     NOT NULL COMMENT '图文内容(富文本/Markdown)',
    `images`        JSON         DEFAULT NULL COMMENT '图片附件(JSON数组)',
    `like_count`    INT          NOT NULL DEFAULT 0 COMMENT '点赞数量',
    `comment_count` INT          NOT NULL DEFAULT 0 COMMENT '评论数量',
    `audit_status`  ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    `reject_reason` VARCHAR(500) DEFAULT NULL COMMENT '驳回理由',
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_audit_status` (`audit_status`),
    CONSTRAINT `fk_post_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成果帖子表';


-- ================================================================
-- 核心表 8: 审核记录表 (audit_log)
-- ================================================================
CREATE TABLE `audit_log` (
    `id`            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '审核ID',
    `auditor_id`    BIGINT       NOT NULL COMMENT '审核员ID(关联user.id)',
    `content_id`    BIGINT       NOT NULL COMMENT '被审核内容ID',
    `content_type`  ENUM('resource','achievement','task_package') NOT NULL COMMENT '内容类型',
    `action`        ENUM('approve','reject') NOT NULL COMMENT '审核操作: approve=通过 reject=驳回',
    `reject_reason` VARCHAR(500) DEFAULT NULL COMMENT '驳回理由',
    `audit_time`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '审核时间',
    PRIMARY KEY (`id`),
    KEY `idx_auditor` (`auditor_id`),
    KEY `idx_content` (`content_id`, `content_type`),
    CONSTRAINT `fk_log_auditor` FOREIGN KEY (`auditor_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审核记录表';


-- ================================================================
-- 支撑表 1: 成果评论表 (achievement_comment)
-- ================================================================
CREATE TABLE `achievement_comment` (
    `id`         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    `post_id`    BIGINT       NOT NULL COMMENT '帖子ID(关联achievement_post.id)',
    `user_id`    BIGINT       NOT NULL COMMENT '评论人ID(关联user.id)',
    `content`    VARCHAR(1000) NOT NULL COMMENT '评论内容',
    `is_teacher` TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否教师专业点评',
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
    PRIMARY KEY (`id`),
    KEY `idx_post` (`post_id`),
    KEY `idx_user` (`user_id`),
    CONSTRAINT `fk_cmt_post` FOREIGN KEY (`post_id`) REFERENCES `achievement_post` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cmt_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成果评论表';


-- ================================================================
-- 支撑表 2: 成果点赞表 (achievement_like)
-- ================================================================
CREATE TABLE `achievement_like` (
    `id`         BIGINT   NOT NULL AUTO_INCREMENT COMMENT '点赞ID',
    `post_id`    BIGINT   NOT NULL COMMENT '帖子ID(关联achievement_post.id)',
    `user_id`    BIGINT   NOT NULL COMMENT '点赞用户ID(关联user.id)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_post_user` (`post_id`, `user_id`),
    CONSTRAINT `fk_like_post` FOREIGN KEY (`post_id`) REFERENCES `achievement_post` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成果点赞表';


-- ================================================================
-- 支撑表 3: 结伴自习房间表 (study_room)
-- ================================================================
CREATE TABLE `study_room` (
    `id`             BIGINT       NOT NULL AUTO_INCREMENT COMMENT '房间ID',
    `name`           VARCHAR(100) NOT NULL COMMENT '房间名称',
    `creator_id`     BIGINT       NOT NULL COMMENT '创建者ID(关联user.id)',
    `target_minutes` INT          NOT NULL DEFAULT 120 COMMENT '目标自习时长(分钟)',
    `is_private`     TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否私密: 0=公开 1=私密',
    `max_members`    INT          NOT NULL DEFAULT 10 COMMENT '最大成员数',
    `status`         ENUM('active','ended') NOT NULL DEFAULT 'active' COMMENT '房间状态',
    `created_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_creator` (`creator_id`),
    KEY `idx_status` (`status`),
    CONSTRAINT `fk_room_creator` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='结伴自习房间表';


-- ================================================================
-- 支撑表 4: 自习房间成员表 (study_room_member)
-- ================================================================
CREATE TABLE `study_room_member` (
    `id`            BIGINT     NOT NULL AUTO_INCREMENT COMMENT '成员记录ID',
    `room_id`       BIGINT     NOT NULL COMMENT '房间ID(关联study_room.id)',
    `user_id`       BIGINT     NOT NULL COMMENT '用户ID(关联user.id)',
    `study_minutes` INT        NOT NULL DEFAULT 0 COMMENT '已自习时长(分钟)',
    `is_studying`   TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否正在自习中',
    `joined_at`     DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_room_user` (`room_id`, `user_id`),
    CONSTRAINT `fk_member_room` FOREIGN KEY (`room_id`) REFERENCES `study_room` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_member_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='自习房间成员表';


-- ================================================================
-- 支撑表 5: 资源收藏表 (user_favorite)
-- ================================================================
CREATE TABLE `user_favorite` (
    `id`          BIGINT   NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
    `user_id`     BIGINT   NOT NULL COMMENT '用户ID(关联user.id)',
    `resource_id` BIGINT   NOT NULL COMMENT '资源ID(关联market_resource.id)',
    `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_resource` (`user_id`, `resource_id`),
    CONSTRAINT `fk_fav_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fav_resource` FOREIGN KEY (`resource_id`) REFERENCES `market_resource` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资源收藏表';


-- ================================================================
-- 支撑表 6: 消息通知表 (message)
-- ================================================================
CREATE TABLE `message` (
    `id`         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `user_id`    BIGINT       NOT NULL COMMENT '接收用户ID(关联user.id)',
    `sender_id`  BIGINT       DEFAULT NULL COMMENT '发送者ID(好友请求等场景)',
    `related_id` BIGINT       DEFAULT NULL COMMENT '关联ID(如friendship.id)',
    `title`      VARCHAR(100) NOT NULL COMMENT '消息标题',
    `content`    VARCHAR(500) NOT NULL COMMENT '消息内容',
    `msg_type`   ENUM('audit','system','comment','like','friend_request','friend_accept') NOT NULL DEFAULT 'system' COMMENT '消息类型',
    `is_read`    TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否已读: 0=未读 1=已读',
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_read` (`user_id`, `is_read`),
    CONSTRAINT `fk_msg_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息通知表';


-- ================================================================
-- 支撑表 7: 好友关系表 (friendship)
-- ================================================================
CREATE TABLE `friendship` (
    `id`           BIGINT      NOT NULL AUTO_INCREMENT COMMENT '关系ID',
    `requester_id` BIGINT      NOT NULL COMMENT '发起者ID(关联user.id)',
    `receiver_id`  BIGINT      NOT NULL COMMENT '接收者ID(关联user.id)',
    `status`       ENUM('pending','accepted','rejected') NOT NULL DEFAULT 'pending' COMMENT '好友状态',
    `created_at`   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_friendship_pair` (`requester_id`, `receiver_id`),
    KEY `idx_fs_receiver` (`receiver_id`, `status`),
    CONSTRAINT `fk_fs_req` FOREIGN KEY (`requester_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fs_rec` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='好友关系表';


-- ================================================================
-- 支撑表 8: 私信会话表 (conversation)
-- ================================================================
CREATE TABLE `conversation` (
    `id`             BIGINT      NOT NULL AUTO_INCREMENT COMMENT '会话ID',
    `user1_id`       BIGINT      NOT NULL COMMENT '用户1 ID(始终为较小ID)',
    `user2_id`       BIGINT      NOT NULL COMMENT '用户2 ID(始终为较大ID)',
    `last_message`   TEXT        DEFAULT NULL COMMENT '最后一条消息内容',
    `last_message_at` DATETIME   DEFAULT NULL COMMENT '最后消息时间',
    `created_at`     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_conversation_users` (`user1_id`, `user2_id`),
    CONSTRAINT `fk_conv_u1` FOREIGN KEY (`user1_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_conv_u2` FOREIGN KEY (`user2_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私信会话表';


-- ================================================================
-- 支撑表 9: 私信消息表 (private_message)
-- ================================================================
CREATE TABLE `private_message` (
    `id`             BIGINT      NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `conversation_id` BIGINT     NOT NULL COMMENT '会话ID(关联conversation.id)',
    `sender_id`      BIGINT      NOT NULL COMMENT '发送者ID(关联user.id)',
    `receiver_id`    BIGINT      NOT NULL COMMENT '接收者ID(关联user.id)',
    `content`        TEXT        NOT NULL COMMENT '消息内容',
    `is_read`        TINYINT(1)  NOT NULL DEFAULT 0 COMMENT '0=未读 1=已读',
    `created_at`     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_pm_conv` (`conversation_id`),
    KEY `idx_pm_receiver` (`receiver_id`, `is_read`),
    CONSTRAINT `fk_pm_conv` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pm_sender` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pm_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私信消息表';


-- ================================================================
-- 种子数据: 全部用户 (26个，密码均为 123456)
-- ID: 1=admin 2=auditor01 3=teacher01 4=student01 5=student02
--     6~18=student03~student15  19=teacher02 20=teacher03
--     21=admin02 22=admin03 23=auditor02 24=auditor03 25=teacher04 26=teacher05
-- ================================================================

INSERT INTO `user` (`username`, `password`, `role`, `nickname`, `avatar`, `real_name`, `teacher_no`, `cert_status`, `status`) VALUES
('admin',      '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'admin',    '超级管理员',   NULL, NULL,      NULL,         'approved', 1),
('auditor01',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'auditor',  '审核员01',     NULL, NULL,      NULL,         'approved', 1),
('teacher01',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher',  '王老师',       NULL, '王明华',   'T20210001',  'approved', 1),
('student01',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '李同学',       NULL, NULL,      NULL,         'none',     1),
('student02',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '赵同学',       NULL, NULL,      NULL,         'none',     1),
('student03',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '陈思雨',       NULL, NULL,      NULL,         'none',     1),
('student04',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '林浩然',       NULL, NULL,      NULL,         'none',     1),
('student05',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '周明月',       NULL, NULL,      NULL,         'none',     1),
('student06',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '吴子轩',       NULL, NULL,      NULL,         'none',     1),
('student07',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '郑悦琳',       NULL, NULL,      NULL,         'none',     1),
('student08',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '王梓涵',       NULL, NULL,      NULL,         'none',     1),
('student09',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '刘佳怡',       NULL, NULL,      NULL,         'none',     1),
('student10',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '黄宇翔',       NULL, NULL,      NULL,         'none',     1),
('student11',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '徐梦瑶',       NULL, NULL,      NULL,         'none',     1),
('student12',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '何俊杰',       NULL, NULL,      NULL,         'none',     1),
('student13',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '罗雨萱',       NULL, NULL,      NULL,         'none',     1),
('student14',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '高志远',       NULL, NULL,      NULL,         'none',     1),
('student15',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student',  '孙嘉怡',       NULL, NULL,      NULL,         'none',     1),
('teacher02',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher',  '李教授',       NULL, '李建国',   'T20180012',  'approved', 1),
('teacher03',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher',  '张老师',       NULL, '张丽华',   'T20190025',  'pending',  1),
('admin02',    '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'admin',    '系统管理员02', NULL, NULL,      NULL,         'approved', 1),
('admin03',    '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'admin',    '系统管理员03', NULL, NULL,      NULL,         'approved', 1),
('auditor02',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'auditor',  '审核员02',     NULL, NULL,      NULL,         'approved', 1),
('auditor03',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'auditor',  '审核员03',     NULL, NULL,      NULL,         'approved', 1),
('teacher04',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher',  '赵教授',       NULL, '赵明阳',   'T20200008',  'approved', 1),
('teacher05',  '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher',  '钱老师',       NULL, '钱秀英',   'T20210030',  'approved', 1);


-- ================================================================
-- 种子数据: 任务包 (14个)
-- ================================================================

INSERT INTO `task_package` (`title`, `category`, `source`, `publisher_id`, `description`, `daily_hours`, `level`, `is_official`, `audit_status`) VALUES
('Python数据分析30天入门',       '技能学习', 'ai_generated',   4,  '从零开始掌握Python数据分析核心技能，覆盖Pandas、NumPy、Matplotlib', 3, 'beginner',     0, 'approved'),
('考研政治马原核心考点精讲',     '考研',     'user_published', 3,  '马克思主义基本原理高频考点系统梳理，配套思维导图', 2, 'intermediate', 1, 'approved'),
('英语四级30天冲刺计划',         '考证',     'ai_generated',   4,  '针对英语四级考试的30天冲刺学习计划，覆盖听力、阅读、写作、翻译四大模块', 3, 'intermediate', 0, 'approved'),
('高等数学微积分入门到精通',     '专业课',   'ai_generated',   5,  '从极限到积分，系统学习微积分核心概念与计算技巧', 4, 'beginner',     0, 'approved'),
('Java后端开发工程师成长路线',   '技能学习', 'ai_generated',   6,  'Java基础到Spring Boot框架，后端开发全栈技能学习计划', 3, 'intermediate', 0, 'approved'),
('考研英语真题精刷计划',         '考研',     'user_published', 4,  '近10年考研英语真题逐套精讲精练，配套解析笔记', 2, 'advanced',     0, 'approved'),
('Python机器学习实战30天',       '技能学习', 'ai_generated',   8,  'Scikit-learn、TensorFlow入门，动手实现经典机器学习项目', 3, 'advanced',     0, 'approved'),
('大学英语语法系统精讲',         '专业课',   'user_published', 19, '从词法到句法，系统梳理英语语法核心知识点，配套练习题', 2, 'beginner',     1, 'approved'),
('数据结构算法面试突击',         '技能学习', 'ai_generated',   9,  '链表、树、图、排序、动态规划，面试常考算法精讲精练', 4, 'intermediate', 0, 'approved'),
('考研数学线性代数全程',         '考研',     'user_published', 5,  '行列式、矩阵、向量组、线性方程组、特征值与特征向量', 3, 'intermediate', 0, 'approved'),
('前端Vue3从入门到实战',         '技能学习', 'ai_generated',   10, 'Vue3组合式API、Vue Router、Pinia状态管理、Element Plus实战', 3, 'beginner',     0, 'approved'),
('教师资格证教育知识速记',       '考证',     'ai_generated',   11, '教育学、心理学核心考点速记，配套真题模拟练习', 2, 'beginner',     0, 'pending'),
('计算机网络原理系统学习',       '专业课',   'user_published', 25, '从物理层到应用层，系统讲解计算机网络OSI七层模型与TCP/IP协议栈', 3, 'intermediate', 1, 'approved'),
('大学英语学术写作入门',         '专业课',   'user_published', 26, '学术论文结构、引用规范、常用句型，提升英语学术写作能力', 2, 'intermediate', 1, 'approved');


-- ================================================================
-- 种子数据: 子任务 (60个)
-- ================================================================

INSERT INTO `task_item` (`package_id`, `name`, `description`, `sort_order`, `estimated_hours`) VALUES
-- 任务包1: Python数据分析30天入门
(1, 'Python环境搭建与基础语法', '安装Anaconda，掌握变量、数据类型、条件循环', 1, 3.0),
(1, 'NumPy数组运算入门', '掌握ndarray创建、索引、广播机制、矩阵运算', 2, 4.0),
(1, 'Pandas数据处理实战', 'DataFrame操作、数据清洗、分组聚合、合并拼接', 3, 5.0),
(1, 'Matplotlib数据可视化', '折线图、柱状图、散点图、子图布局、样式美化', 4, 3.0),
(1, '综合项目：销售数据分析报告', '运用所学完成一份完整的数据分析报告', 5, 6.0),
-- 任务包2: 考研政治马原核心考点精讲
(2, '马原绪论：马克思主义概述', '掌握马克思主义的科学内涵与理论来源', 1, 2.0),
(2, '唯物论：物质与意识', '理解物质观、意识观、主观能动性', 2, 2.5),
(2, '辩证法：对立统一规律', '掌握矛盾分析法、质量互变、否定之否定', 3, 3.0),
-- 任务包3: 英语四级30天冲刺计划
(3, '四级听力短对话专项训练', '掌握短对话常见场景词汇，练习抓取关键信息', 1, 2.0),
(3, '四级听力长对话与短文', '训练长对话和短文听力的笔记技巧', 2, 3.0),
(3, '四级阅读仔细阅读精练', '掌握仔细阅读题型解题步骤，提高准确率', 3, 2.5),
(3, '四级阅读快速阅读技巧', '训练快速定位信息、略读扫读能力', 4, 2.0),
(3, '四级写作模板与范文背诵', '积累写作模板，背诵高分范文10篇', 5, 3.0),
(3, '四级翻译专项突破', '掌握汉译英常见句型与翻译技巧', 6, 2.0),
(3, '四级全真模拟测试', '完成5套全真模拟题，查漏补缺', 7, 5.0),
-- 任务包4: 高等数学微积分入门到精通
(4, '极限的概念与计算', '理解极限定义，掌握极限计算方法', 1, 3.0),
(4, '连续性与间断点', '掌握函数连续性判定与间断点分类', 2, 2.0),
(4, '导数与微分', '理解导数几何意义，掌握求导法则', 3, 4.0),
(4, '微分中值定理', '理解罗尔定理、拉格朗日中值定理', 4, 3.0),
(4, '不定积分计算', '掌握换元法、分部积分法', 5, 4.0),
(4, '定积分及应用', '掌握定积分计算与几何应用', 6, 4.0),
-- 任务包5: Java后端开发工程师成长路线
(5, 'Java基础语法复习', '变量、控制流、数组、方法', 1, 3.0),
(5, '面向对象编程OOP', '类与对象、继承、多态、接口', 2, 5.0),
(5, '集合框架', 'List、Set、Map的使用与原理', 3, 4.0),
(5, '多线程与并发', '线程创建、同步、线程池', 4, 5.0),
(5, 'MySQL与JDBC', '数据库连接、CRUD操作、连接池', 5, 3.0),
(5, 'Spring Boot框架入门', 'IoC、AOP、RESTful API开发', 6, 6.0),
-- 任务包6: 考研英语真题精刷计划
(6, '2015年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 1, 4.0),
(6, '2016年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 2, 4.0),
(6, '2017年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 3, 4.0),
(6, '2018年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 4, 4.0),
(6, '高频词汇专项突破', '考研核心词汇3000精讲', 5, 6.0),
-- 任务包7: Python机器学习实战30天
(7, 'NumPy科学计算基础', '数组操作、线性代数、随机数', 1, 3.0),
(7, 'Pandas数据分析', 'DataFrame操作、数据清洗、分组聚合', 2, 4.0),
(7, 'Matplotlib数据可视化', '折线图、散点图、热力图绘制', 3, 2.0),
(7, 'Scikit-learn线性回归', '简单线性回归、多元线性回归实战', 4, 4.0),
(7, '逻辑回归与分类', '二分类、多分类、模型评估', 5, 4.0),
(7, '决策树与随机森林', '决策树原理、随机森林集成学习', 6, 4.0),
(7, '神经网络入门', 'TensorFlow/Keras搭建简单神经网络', 7, 5.0),
-- 任务包8: 数据结构算法面试突击
(8, '数组与链表', '动态数组、单链表、双链表操作', 1, 3.0),
(8, '栈与队列', '栈的应用、队列的实现、单调栈', 2, 3.0),
(8, '二叉树遍历', '前序、中序、后序、层序遍历', 3, 3.0),
(8, '排序算法', '快排、归并、堆排序及复杂度分析', 4, 4.0),
(8, '二分查找', '二分查找变体、旋转数组查找', 5, 2.0),
(8, '动态规划入门', '背包问题、最长子序列、路径问题', 6, 5.0),
(8, '图论基础', 'BFS、DFS、最短路径、拓扑排序', 7, 5.0),
-- 任务包9: 考研数学线性代数全程
(9, '行列式计算', '行列式性质、展开定理、克莱默法则', 1, 3.0),
(9, '矩阵运算', '矩阵乘法、逆矩阵、秩', 2, 4.0),
(9, '向量组线性相关性', '线性组合、线性相关与无关、极大无关组', 3, 4.0),
(9, '线性方程组', '齐次/非齐次方程组解的结构', 4, 4.0),
(9, '特征值与特征向量', '特征值求解、相似矩阵、对角化', 5, 5.0),
-- 任务包10: 前端Vue3从入门到实战
(10, 'HTML/CSS/JS基础回顾', '前端三件套核心知识快速复习', 1, 3.0),
(10, 'Vue3组合式API', 'setup、ref、reactive、computed', 2, 4.0),
(10, 'Vue Router路由管理', '路由配置、嵌套路由、导航守卫', 3, 3.0),
(10, 'Pinia状态管理', 'store定义、状态读写、actions', 4, 3.0),
(10, 'Element Plus组件库', '表单、表格、弹窗、分页组件使用', 5, 4.0),
(10, 'Vue3项目实战', '从零搭建一个完整后台管理系统', 6, 6.0),
-- 任务包13: 计算机网络原理系统学习
(13, '计算机网络概述', '了解计算机网络发展历程、分类、性能指标', 1, 2.0),
(13, '物理层基础', '数据通信基础、信道复用技术、物理层设备', 2, 3.0),
(13, '数据链路层', 'MAC协议、CSMA/CD、交换机工作原理', 3, 4.0),
(13, '网络层与IP协议', 'IP地址、子网划分、路由算法、ICMP', 4, 5.0),
(13, '传输层TCP/UDP', 'TCP三次握手、流量控制、拥塞控制', 5, 5.0),
(13, '应用层协议', 'HTTP、DNS、SMTP、FTP协议详解', 6, 4.0),
-- 任务包14: 大学英语学术写作入门
(14, '学术论文结构', 'IMRD结构：引言、方法、结果、讨论', 1, 2.0),
(14, '引用规范与格式', 'APA、MLA、Chicago引用格式详解', 2, 3.0),
(14, '学术写作常用句型', '引言、方法、结果、讨论各部分高频句型', 3, 3.0),
(14, '摘要写作技巧', '摘要的结构要素与写作规范', 4, 2.0),
(14, '学术写作实战练习', '完成一篇完整的学术小论文', 5, 6.0);


-- ================================================================
-- 种子数据: 资源集市 (17个)
-- ================================================================

INSERT INTO `market_resource` (`title`, `category`, `content`, `publisher_id`, `publisher_role`, `is_teacher_certified`, `audit_status`, `view_count`) VALUES
('Python数据分析完整学习路线图', '技能学习', '# Python数据分析学习路线\n\n## 第一阶段：基础\n- Python语法基础\n- NumPy数组运算\n\n## 第二阶段：核心\n- Pandas数据处理\n- 数据可视化', 4, 'student', 0, 'approved', 89),
('2026考研政治高频考点汇总', '考研', '# 考研政治高频考点\n\n## 马原部分\n1. 物质与意识的辩证关系\n2. 对立统一规律\n3. 实践与认识', 3, 'teacher', 1, 'approved', 120),
('英语四级高频词汇1800整理版', '考证', '# 四级高频词汇1800\n\n## A开头\n- abandon v.放弃\n- ability n.能力\n- abroad adv.在国外\n\n## B开头\n- background n.背景\n- balance n.平衡\n\n（完整版见附件）', 4, 'student', 0, 'approved', 156),
('微积分公式大全（手写笔记）', '专业课', '# 微积分公式汇总\n\n## 导数公式\n- (sinx)\' = cosx\n- (cosx)\' = -sinx\n- (e^x)\' = e^x\n- (lnx)\' = 1/x\n\n## 积分公式\n- ∫cosx dx = sinx + C\n- ∫sinx dx = -cosx + C', 5, 'student', 0, 'approved', 203),
('Java面试题100道精选', '技能学习', '# Java面试高频100题\n\n## 基础篇\n1. ==和equals的区别\n2. String为什么不可变\n3. HashMap底层原理\n\n## 并发篇\n4. synchronized和Lock区别\n5. volatile关键字原理', 6, 'student', 0, 'approved', 389),
('考研政治思修法基思维导图', '考研', '# 思想道德修养与法律基础\n\n## 绪论\n- 思想道德与法律的关系\n\n## 理想信念篇\n- 理想的分类\n- 信念的特征\n- 理想信念的作用', 5, 'student', 0, 'approved', 98),
('Python爬虫入门到精通教程', '技能学习', '# Python爬虫教程\n\n## 第一章 爬虫基础\n- HTTP/HTTPS协议\n- requests库入门\n\n## 第二章 数据解析\n- BeautifulSoup\n- XPath\n- 正则表达式', 8, 'student', 0, 'approved', 267),
('大学英语四级听力技巧总结', '考证', '# 四级听力技巧\n\n## 短对话\n1. 听关键词：but, however, instead\n2. 注意语气转折\n3. 场景词汇积累\n\n## 长对话\n1. 预读选项\n2. 边听边记\n3. 重点关注首尾', 4, 'student', 0, 'approved', 178),
('Spring Boot项目实战源码', '技能学习', '# Spring Boot实战项目\n\n## 项目介绍\n基于Spring Boot + MyBatis + MySQL的后台管理系统\n\n## 技术栈\n- Spring Boot 2.7\n- MyBatis Plus\n- MySQL 8.0\n- JWT鉴权', 9, 'student', 0, 'approved', 312),
('数据结构考研复习笔记', '专业课', '# 数据结构复习笔记\n\n## 第一章 绪论\n- 时间复杂度分析\n- 空间复杂度分析\n\n## 第二章 线性表\n- 顺序表\n- 链表\n- 栈和队列', 10, 'student', 0, 'approved', 145),
('前端Vue3学习路线图2026版', '技能学习', '# Vue3学习路线\n\n## 第一阶段 基础\n- HTML/CSS/JavaScript\n- ES6+语法\n\n## 第二阶段 Vue3\n- 组合式API\n- 组件通信\n- 生命周期', 10, 'student', 0, 'approved', 198),
('考研英语长难句解析100句', '考研', '# 考研长难句100句\n\n## 第1句\nThe OECD estimates that in the 27 developed economies, the average unemployment rate will reach 10% by 2014.\n\n**解析**：\n- 主干：The OECD estimates that...\n- that引导宾语从句', 4, 'student', 0, 'approved', 234),
('教师资格证教育学重点笔记', '考证', '# 教育学重点\n\n## 第一章 教育与教育学\n- 教育的概念\n- 教育的起源\n- 教育学的发展\n\n## 第二章 教育目的\n- 教育目的的概念\n- 个人本位论与社会本位论', 11, 'student', 0, 'approved', 87),
('高等数学期末复习题含答案', '专业课', '# 高数期末复习题\n\n## 一、选择题\n1. 设f(x)=x^2，则f\'(2)=？\nA. 2  B. 4  C. 8  D. 0\n\n**答案：B**\n\n2. 下列哪个函数在x=0处连续？\nA. 1/x  B. sin(1/x)  C. |x|  D. ln(x)', 14, 'student', 0, 'approved', 256),
('机器学习算法对比总结表', '技能学习', '# 机器学习算法对比\n\n| 算法 | 类型 | 优点 | 缺点 | 适用场景 |\n|------|------|------|------|----------|\n| 线性回归 | 监督 | 简单快速 | 欠拟合 | 连续值预测 |\n| 决策树 | 监督 | 可解释 | 过拟合 | 分类 |\n| KNN | 监督 | 无需训练 | 计算量大 | 分类回归 |', 8, 'student', 0, 'pending', 0),
('计算机网络OSI七层模型详解', '专业课', '# OSI七层模型详解\n\n## 物理层\n- 传输比特流\n- 关注信号编码、传输介质\n\n## 数据链路层\n- MAC地址寻址\n- CSMA/CD协议\n- 交换机工作原理\n\n## 网络层\n- IP协议\n- 路由选择\n- ICMP协议\n\n## 传输层\n- TCP三次握手\n- UDP无连接\n\n## 应用层\n- HTTP/HTTPS\n- DNS\n- SMTP/FTP', 25, 'teacher', 1, 'approved', 178),
('英语学术写作常用句型100例', '专业课', '# 学术写作高频句型\n\n## 引言部分\n1. This paper aims to investigate...\n2. Recent studies have shown that...\n3. However, little attention has been paid to...\n\n## 方法部分\n1. The experiment was conducted using...\n2. Data were collected from...\n3. Statistical analysis was performed using...\n\n## 结果部分\n1. The results indicate that...\n2. As shown in Figure 1...\n3. There was a significant difference between...\n\n## 讨论部分\n1. These findings suggest that...\n2. This is consistent with previous research...\n3. One limitation of this study is...', 26, 'teacher', 1, 'approved', 145);


-- ================================================================
-- 种子数据: 成果帖子 (17个)
-- ================================================================

INSERT INTO `achievement_post` (`user_id`, `content`, `like_count`, `comment_count`, `audit_status`) VALUES
(4,  '今天完成了Python数据分析第一周的学习，整理了一份思维导图分享给大家！涵盖了NumPy和Pandas的核心API，有需要的同学可以评论区留言~', 15, 3, 'approved'),
(5,  '考研倒计时100天！今天复习了马原的辩证法部分，对立统一规律真的需要反复理解，分享我的笔记截图', 8, 2, 'approved'),
(4,  '坚持打卡第7天！今天完成了Python数据分析的Pandas模块学习，整理了DataFrame操作的速查表分享给大家，常用操作一目了然！', 32, 5, 'approved'),
(5,  '考研倒计时90天！今天做了2018年考研英语真题，阅读理解错了4个，感觉还需加强长难句分析能力，分享一下今天的笔记', 18, 3, 'approved'),
(6,  'Java多线程学完了！用synchronized和ReentrantLock分别实现了线程安全的单例模式，对比了两种方式的性能差异，发现Lock效率更高', 45, 8, 'approved'),
(7,  '英语四级听力从120分提升到180分的方法：每天精听30分钟+泛听1小时，坚持一个月效果显著！分享我的听力训练计划表', 67, 12, 'approved'),
(8,  '用Scikit-learn完成了第一个机器学习项目——波士顿房价预测！线性回归模型R2达到0.73，虽然不算高但很有成就感，附上代码和思路', 89, 15, 'approved'),
(9,  '数据结构算法刷完了LeetCode前100题！总结一下高频考点：二叉树遍历、动态规划、BFS/DFS。分享我的刷题笔记和解题模板', 56, 9, 'approved'),
(10, 'Vue3项目上线了！用Vue3+Element Plus做了一个后台管理系统，包含登录鉴权、表格CRUD、权限管理。源码已开源，欢迎交流', 73, 11, 'approved'),
(11, '教师资格证笔试一次过！教育知识与能力87分，分享我的备考经验：重点背诵教育学原理和心理学概念，配合真题模拟', 41, 6, 'approved'),
(12, '高数微积分期末考了92分！分享一下我的学习方法：上课认真听讲+课后及时复习+大量刷题。微积分的关键是理解极限思想', 38, 7, 'approved'),
(13, '今天用Python爬虫抓取了豆瓣Top250电影数据，做了数据清洗和可视化分析，发现了评分分布的一些有趣规律，附上分析报告', 52, 8, 'approved'),
(14, '线性代数矩阵运算总结：行列式、逆矩阵、秩的求解方法整理成思维导图了，考前复习效率翻倍！', 29, 4, 'approved'),
(15, '前端面试复盘：今天面试了某互联网公司，问了Vue3组合式API原理、虚拟DOM diff算法、前端性能优化方案，分享我的回答思路', 64, 10, 'approved'),
(4,  '考研政治马原部分学完了！唯物论、辩证法、认识论三大板块的思维导图整理完毕。发现用框架图记忆比死记硬背效率高太多', 35, 5, 'approved'),
(25, '期末复习资料整理完毕！计算机网络各章节重点知识思维导图已上传，涵盖OSI七层模型、TCP/IP协议栈、路由算法等核心考点，希望对同学们的复习有帮助', 52, 7, 'approved'),
(26, '学术写作课程结课了！整理了一份英语学术论文写作全流程指南，从选题、文献综述到引用格式，帮助大家规避常见的写作误区', 38, 5, 'approved');


-- ================================================================
-- 种子数据: 成果评论 (33个)
-- ================================================================

INSERT INTO `achievement_comment` (`post_id`, `user_id`, `content`, `is_teacher`) VALUES
(1,  5,  '思维导图做得太清晰了，感谢分享！', 0),
(1,  3,  '整理得很系统，建议补充数据清洗部分的实战案例，会更有参考价值。', 1),
(2,  4,  '加油！坚持就是胜利！', 0),
(3,  5,  'DataFrame速查表太实用了，正需要这个！', 0),
(3,  19, '整理得很系统，建议补充merge和concat的区别说明，这是面试常考点。', 1),
(3,  8,  '感谢分享！收藏了', 0),
(4,  4,  '阅读理解确实需要加强长难句分析，推荐田静老师的语法课', 0),
(4,  6,  '同考研党，一起加油！你的笔记很有参考价值', 0),
(5,  10, 'ReentrantLock确实比synchronized灵活，但要注意手动释放锁', 0),
(5,  4,  '请问性能差异具体是多少？有测试数据吗？', 0),
(5,  19, '补充一点：synchronized是JVM层面，ReentrantLock是API层面，使用场景有区别。总结得不错。', 1),
(6,  8,  '精听+泛听的组合方法很科学，我也用这个方法提升了不少', 0),
(6,  11, '听力训练计划表能分享一下吗？谢谢', 0),
(7,  6,  '波士顿房价预测是经典项目！可以试试特征工程提升R2', 0),
(7,  9,  '代码能开源吗？想学习一下你的实现思路', 0),
(7,  19, 'R2=0.73作为入门项目不错，可以尝试加入正则化或使用随机森林对比效果。', 1),
(7,  5,  '机器学习入门最佳项目之一！', 0),
(8,  4,  'LeetCode前100题含金量很高，感谢分享笔记', 0),
(8,  7,  '动态规划确实是最难的，你的解题模板很实用', 0),
(9,  6,  '源码地址求分享！想学习一下你的项目结构', 0),
(9,  10, 'Vue3+Element Plus确实是后台管理系统的最佳实践', 0),
(10, 11, '教资笔记求分享！我也在备考', 0),
(11, 5,  '92分太强了！微积分确实需要大量刷题', 0),
(12, 8,  '豆瓣爬虫分析很有趣，可视化部分用的什么库？', 0),
(13, 14, '思维导图方式记忆确实高效！', 0),
(14, 10, '前端面试题总结得很全面，收藏了', 0),
(14, 6,  '虚拟DOM diff算法是面试必考，了解key的作用很关键', 0),
(15, 5,  '框架图记忆法确实比死记硬背好太多，感谢分享', 0),
(16, 6,  'OSI七层模型思维导图太清晰了！期末复习救星', 0),
(16, 9,  '路由算法部分讲得很透彻，感谢赵教授分享', 0),
(16, 26, '补充一点：建议同学们重点关注TCP三次握手和四次挥手，这是面试和考试的高频考点', 1),
(17, 4,  '学术写作指南非常实用，引用格式部分解决了我的大问题', 0),
(17, 25, '写作流程图很清晰，建议增加文献管理工具的使用教程', 1);


-- ================================================================
-- 种子数据: 点赞 (63个)
-- ================================================================

INSERT INTO `achievement_like` (`post_id`, `user_id`) VALUES
(1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
(2, 4), (2, 5), (2, 6),
(3, 5), (3, 6), (3, 7), (3, 8), (3, 19),
(4, 4), (4, 6), (4, 10),
(5, 4), (5, 7), (5, 9), (5, 10),
(6, 4), (6, 5), (6, 8), (6, 9), (6, 11),
(7, 5), (7, 6), (7, 9), (7, 10), (7, 12), (7, 13),
(8, 4), (8, 6), (8, 7), (8, 10), (8, 11),
(9, 5), (9, 8), (9, 10), (9, 13),
(10, 4), (10, 6), (10, 11),
(11, 5), (11, 8), (11, 14),
(12, 6), (12, 7), (12, 9), (12, 10),
(13, 4), (13, 5), (13, 14),
(14, 5), (14, 8), (14, 10), (14, 11),
(15, 5), (15, 6), (15, 7),
(16, 4), (16, 5), (16, 6), (16, 7), (16, 8), (16, 9), (16, 10),
(17, 4), (17, 5), (17, 6), (17, 11), (17, 12);


-- ================================================================
-- 种子数据: 打卡记录 (18个)
-- ================================================================

INSERT INTO `check_record` (`user_id`, `task_id`, `status`, `remark`, `check_time`) VALUES
(4, 1,  'completed', '环境搭建完成，Python基础语法过完了一遍', '2026-08-05 10:30:00'),
(4, 2,  'completed', 'NumPy数组运算学完了，广播机制还需要再理解', '2026-08-06 14:20:00'),
(4, 3,  'completed', 'Pandas数据处理实战完成，DataFrame操作熟练了', '2026-08-07 09:15:00'),
(4, 4,  'completed', 'Matplotlib可视化画了几个图表，效果不错', '2026-08-08 16:45:00'),
(4, 5,  'completed', '综合项目完成！数据分析报告写完了', '2026-08-09 20:00:00'),
(5, 6,  'completed', '马原绪论学完，理解了马克思主义的科学内涵', '2026-08-05 11:00:00'),
(5, 7,  'completed', '唯物论部分搞定，物质与意识的辩证关系是重点', '2026-08-06 15:30:00'),
(5, 8,  'completed', '辩证法对立统一规律，矛盾分析法需要反复理解', '2026-08-07 19:00:00'),
(6, 9,  'completed', '听力短对话训练50题，正确率提升到80%', '2026-08-06 10:00:00'),
(6, 10, 'completed', '长对话听力练习，笔记技巧很实用', '2026-08-07 14:00:00'),
(6, 11, 'completed', '仔细阅读精练8篇，掌握了定位法', '2026-08-08 16:00:00'),
(5, 16, 'completed', '极限计算方法掌握了，等价无穷小很实用', '2026-08-05 09:30:00'),
(5, 17, 'completed', '连续性和间断点分类搞清楚了', '2026-08-06 13:00:00'),
(5, 18, 'completed', '求导法则练了很多题，复合函数求导要细心', '2026-08-07 15:00:00'),
(5, 19, 'completed', '中值定理理解了，证明题还需要多练', '2026-08-08 17:30:00'),
(6, 22, 'completed', 'Java基础语法复习完，跟C++对比学习效率高', '2026-08-06 10:30:00'),
(6, 23, 'completed', 'OOP四大特性理解了，多态的实际应用还需练习', '2026-08-07 14:30:00'),
(6, 24, 'completed', '集合框架源码看了ArrayList和HashMap', '2026-08-08 16:00:00');


-- ================================================================
-- 种子数据: 学习笔记 (6个)
-- ================================================================

INSERT INTO `note` (`user_id`, `package_id`, `title`, `content`, `is_public`) VALUES
(4, 1, 'Python数据分析学习笔记', '# Python数据分析笔记\n\n## NumPy核心\n- ndarray创建：np.array(), np.zeros(), np.ones()\n- 数组索引：支持布尔索引和花式索引\n- 广播机制：不同形状数组运算规则\n\n## Pandas核心\n- DataFrame创建与索引\n- 数据清洗：dropna(), fillna()\n- 分组聚合：groupby() + agg()', 1),
(4, 1, 'Pandas速查表', '# Pandas常用操作\n\n```python\n# 读取数据\ndf = pd.read_csv("data.csv")\n\n# 查看数据\ndf.head()        # 前5行\ndf.info()        # 数据信息\ndf.describe()    # 统计描述\n\n# 数据筛选\ndf[df["age"] > 18]\ndf.query("age > 18")\n\n# 分组聚合\ndf.groupby("city")["salary"].mean()\n```', 1),
(5, 2, '考研政治马原笔记', '# 马原核心考点\n\n## 唯物论\n1. 物质决定意识，意识对物质有能动作用\n2. 物质的唯一特性是客观实在性\n\n## 辩证法\n1. 对立统一规律是唯物辩证法的实质和核心\n2. 量变和质变的辩证关系\n3. 否定之否定规律\n\n## 认识论\n1. 实践是认识的基础\n2. 真理的绝对性和相对性', 1),
(6, 3, '英语四级备考心得', '# 四级备考笔记\n\n## 听力技巧\n- 预读选项，预判话题\n- 听关键词：but, however, instead\n- 注意数字、时间、地点\n\n## 阅读技巧\n- 先看题目再看文章\n- 定位关键词\n- 仔细阅读注意同义替换', 0),
(5, 4, '微积分公式整理', '# 微积分公式大全\n\n## 基本求导公式\n- (x^n)\' = nx^(n-1)\n- (sinx)\' = cosx\n- (cosx)\' = -sinx\n- (e^x)\' = e^x\n- (lnx)\' = 1/x\n\n## 基本积分公式\n- ∫x^n dx = x^(n+1)/(n+1) + C\n- ∫1/x dx = lnx + C\n- ∫e^x dx = e^x + C\n- ∫cosx dx = sinx + C\n\n## 常用等价无穷小\n- sinx ~ x\n- tanx ~ x\n- 1-cosx ~ x^2/2', 1),
(6, 5, 'Java集合框架笔记', '# Java集合框架\n\n## List\n- ArrayList：底层数组，查询快\n- LinkedList：底层链表，增删快\n\n## Set\n- HashSet：无序，不允许重复\n- TreeSet：自动排序\n\n## Map\n- HashMap：key-value存储，允许null\n- TreeMap：按key排序\n\n## 面试常问\n- HashMap底层：数组+链表+红黑树\n- 扩容机制：初始16，负载因子0.75', 1);


-- ================================================================
-- 种子数据: 资源收藏 (22个)
-- ================================================================

INSERT INTO `user_favorite` (`user_id`, `resource_id`) VALUES
(4, 3), (4, 5), (4, 7), (4, 9),
(5, 1), (5, 4), (5, 11),
(6, 3), (6, 7), (6, 10),
(7, 1), (7, 6), (7, 9),
(8, 5), (8, 7), (8, 13),
(9, 3), (9, 7), (9, 8),
(10, 9), (10, 10), (10, 7);


-- ================================================================
-- 种子数据: 消息通知 (16个)
-- ================================================================

INSERT INTO `message` (`user_id`, `title`, `content`, `msg_type`, `is_read`) VALUES
(4,  '审核通过',   '您发布的资源《Python数据分析完整学习路线图》已审核通过，现已上线资源集市', 'audit',   1),
(4,  '收到新评论', '王老师评论了你的成果《Pandas速查表分享》', 'comment', 0),
(4,  '收到新点赞', '陈思雨等5人点赞了你的成果帖子', 'like',    0),
(5,  '审核通过',   '您发布的资源《考研政治高频考点汇总》已审核通过', 'audit',   1),
(5,  '审核驳回',   '您发布的资源《测试资源》因内容不完整被驳回，请补充后重新提交', 'audit',   0),
(6,  '收到新评论', '林浩然评论了你的成果帖', 'comment', 0),
(7,  '系统通知',   '欢迎加入个人成长学习平台！完善个人信息可获得更好体验', 'system',  1),
(8,  '收到新点赞', '周明月等8人点赞了你的成果帖', 'like',    0),
(9,  '审核通过',   '您发布的资源《Spring Boot项目实战源码》已审核通过', 'audit',   1),
(10, '收到新评论', '吴子轩评论了你的成果帖', 'comment', 0),
(25, '资源审核通过', '您发布的资源《计算机网络OSI七层模型详解》已审核通过', 'audit',   1),
(25, '收到新评论',   '钱老师评论了您的成果帖', 'comment', 0),
(26, '资源审核通过', '您发布的资源《英语学术写作常用句型100例》已审核通过', 'audit',   1),
(26, '收到新点赞',   '李同学等5人点赞了您的成果帖', 'like',    0),
(23, '系统通知',     '您有新的审核任务待处理，请及时查看', 'system',  0),
(24, '系统通知',     '您有新的审核任务待处理，请及时查看', 'system',  0);


-- ================================================================
-- 种子数据: 结伴自习房间 (6个) + 成员 (22个)
-- ================================================================

INSERT INTO `study_room` (`name`, `creator_id`, `target_minutes`, `is_private`, `max_members`, `status`) VALUES
('考研冲刺自习室', 5, 240, 0, 20, 'active'),
('Python学习打卡群', 4, 120, 0, 15, 'active'),
('英语四级备考自习', 7, 180, 0, 10, 'active'),
('Java后端学习小组', 6, 200, 0, 12, 'active'),
('前端进阶自习室', 10, 150, 0, 8, 'active'),
('考研数学刷题营', 5, 300, 0, 15, 'active');

INSERT INTO `study_room_member` (`room_id`, `user_id`, `study_minutes`, `is_studying`) VALUES
(1, 5, 480, 0), (1, 4, 360, 0), (1, 8, 420, 0), (1, 11, 300, 0),
(2, 4, 540, 1), (2, 6, 420, 0), (2, 8, 360, 0), (2, 9, 240, 0),
(3, 7, 360, 0), (3, 11, 300, 0), (3, 13, 240, 0),
(4, 6, 600, 0), (4, 9, 480, 0), (4, 10, 360, 0),
(5, 10, 420, 0), (5, 12, 300, 0), (5, 15, 240, 0),
(6, 5, 720, 0), (6, 14, 480, 0),
(1, 25, 360, 0),
(3, 26, 240, 0),
(6, 25, 480, 0);


-- ================================================================
-- 种子数据: 审核记录 (29个)
-- ================================================================

INSERT INTO `audit_log` (`auditor_id`, `content_id`, `content_type`, `action`, `reject_reason`) VALUES
-- auditor01 (ID=2)
(2,  1, 'resource',    'approve', NULL),
(2,  2, 'resource',    'approve', NULL),
(2,  1, 'achievement', 'approve', NULL),
(2,  2, 'achievement', 'approve', NULL),
(2,  3, 'resource',    'approve', NULL),
(2,  4, 'resource',    'approve', NULL),
(2,  5, 'resource',    'approve', NULL),
(2,  6, 'resource',    'approve', NULL),
(2,  7, 'resource',    'approve', NULL),
(2,  8, 'resource',    'approve', NULL),
(2,  13, 'resource',   'reject',  '内容缺少具体代码示例，请补充完整后重新提交'),
(2,  3, 'achievement', 'approve', NULL),
(2,  4, 'achievement', 'approve', NULL),
(2,  5, 'achievement', 'approve', NULL),
-- auditor02 (ID=23)
(23, 9,  'resource',    'approve', NULL),
(23, 10, 'resource',    'approve', NULL),
(23, 11, 'resource',    'approve', NULL),
(23, 12, 'resource',    'approve', NULL),
(23, 6,  'achievement', 'approve', NULL),
(23, 7,  'achievement', 'approve', NULL),
(23, 14, 'resource',    'reject',  '资源内容排版不规范，请使用标准Markdown格式重新编辑后提交'),
-- auditor03 (ID=24)
(24, 14, 'resource',    'approve', NULL),
(24, 15, 'resource',    'approve', NULL),
(24, 16, 'resource',    'approve', NULL),
(24, 17, 'resource',    'approve', NULL),
(24, 8,  'achievement', 'approve', NULL),
(24, 9,  'achievement', 'approve', NULL),
(24, 16, 'achievement', 'approve', NULL),
(24, 17, 'achievement', 'approve', NULL);


-- ================================================================
-- 补充种子数据: 更多待审核内容 (让审核中心有丰富内容可看)
-- ================================================================

-- 待审核资源 (3个，内容各异)
INSERT INTO `market_resource` (`title`, `category`, `content`, `publisher_id`, `publisher_role`, `is_teacher_certified`, `audit_status`, `view_count`) VALUES
('React Native跨平台移动开发指南', '技能学习', '# React Native入门指南\n\n## 环境搭建\n- Node.js 18+\n- React Native CLI\n- Android Studio / Xcode\n\n## 核心概念\n- 组件化开发\n- Props与State\n- 生命周期方法\n- Flexbox布局\n\n## 实战项目\n- 天气预报App\n- 待办事项应用', 6, 'student', 0, 'pending', 0),
('考研英语写作高分模板20篇', '考研', '# 考研英语写作模板\n\n## 大作文模板\n### 模板一：社会现象类\nAs is vividly depicted in the picture...\n\n### 模板二：哲理启示类\nThe set of drawings above vividly describes...\n\n## 小作文模板\n### 建议信\nDear Sir/Madam,\nI am writing to express my views on...\n\n### 投诉信\nI am writing to bring to your attention...', 5, 'student', 0, 'pending', 0),
('数据结构与算法图解笔记（完整版）', '专业课', '# 数据结构图解笔记\n\n## 第一章 线性表\n### 顺序表\n- 逻辑结构：一对一\n- 存储结构：连续内存\n- 时间复杂度：查找O(1)，插入删除O(n)\n\n### 链表\n- 单链表：指针连接\n- 双链表：前后指针\n- 循环链表：尾指向头\n\n## 第二章 栈与队列\n### 栈\n- LIFO后进先出\n- 应用：括号匹配、表达式求值、递归\n\n## 第三章 树\n### 二叉树\n- 前序/中序/后序遍历\n- 层序遍历（BFS）\n- 二叉搜索树BST', 9, 'student', 0, 'pending', 0);

-- 待审核成果帖子 (3个，内容各异)
INSERT INTO `achievement_post` (`user_id`, `content`, `like_count`, `comment_count`, `audit_status`) VALUES
(6,  '今天用React Native做了一个天气预报App！用了OpenWeatherMap的API，实现了城市搜索、实时天气展示、7天预报功能。踩了不少坑，主要是Android和iOS样式适配的问题，最后用Platform.select解决了。附上项目截图和核心代码~', 0, 0, 'pending'),
(7,  '考研英语写作总结了20个高分模板，涵盖社会现象类、哲理启示类、图表类等常考题型。每个模板都配有范文和亮点句型。亲测有效，去年考研英语一作文拿了18分！分享给大家，祝大家考研顺利！', 0, 0, 'pending'),
(8,  '数据结构期末复习笔记完整版来啦！用思维导图整理了线性表、栈队列、树、图、排序、查找全部章节。每个数据结构都画了图解，标注了时间复杂度。考前刷一遍，期末满分不是梦！PDF版已上传', 0, 0, 'pending');

-- 待审核任务包 (1个，与已有的pending任务包内容不同)
INSERT INTO `task_package` (`title`, `category`, `source`, `publisher_id`, `description`, `daily_hours`, `level`, `is_official`, `audit_status`) VALUES
('Go语言后端开发15天速成', '技能学习', 'ai_generated', 12, '从Go基础语法到Gin框架，15天掌握Go后端开发核心技能，适合有编程基础的开发者', 3, 'intermediate', 0, 'pending');


-- ================================================================
-- 种子数据: 好友关系 (学生之间)
-- ================================================================

INSERT INTO `friendship` (`requester_id`, `receiver_id`, `status`) VALUES
(4, 5, 'accepted'),
(4, 6, 'accepted'),
(5, 6, 'accepted'),
(7, 8, 'accepted'),
(9, 10, 'accepted'),
(4, 7, 'accepted'),
(5, 9, 'accepted'),
(6, 10, 'accepted'),
(11, 12, 'accepted'),
(8, 13, 'accepted'),
-- 2个待处理请求
(14, 4, 'pending'),
(15, 5, 'pending');


-- ================================================================
-- 种子数据: 私信会话与消息
-- ================================================================

INSERT INTO `conversation` (`id`, `user1_id`, `user2_id`, `last_message`, `last_message_at`) VALUES
(1, 4, 5, '好的，明天图书馆见！', '2026-08-10 21:30:00'),
(2, 4, 6, 'Pandas那个问题解决了吗？', '2026-08-09 15:20:00'),
(3, 5, 6, '考研真题我发你了，注意查收', '2026-08-08 19:45:00'),
(4, 7, 8, '四级听力技巧分享给你了', '2026-08-07 14:10:00');

INSERT INTO `private_message` (`conversation_id`, `sender_id`, `receiver_id`, `content`, `is_read`, `created_at`) VALUES
-- 会话1: student01(4) ↔ student02(5)
(1, 4, 5, '同学，Python数据分析那个任务包你学到哪了？', 1, '2026-08-10 20:00:00'),
(1, 5, 4, '我刚学完Pandas，正在做综合项目', 1, '2026-08-10 20:15:00'),
(1, 4, 5, '那个综合项目难吗？我还没开始', 1, '2026-08-10 20:30:00'),
(1, 5, 4, '还好，主要是数据清洗比较费时间。有问题随时问我', 1, '2026-08-10 20:45:00'),
(1, 4, 5, '好的，明天图书馆见！', 0, '2026-08-10 21:30:00'),
-- 会话2: student01(4) ↔ student03(6)
(2, 6, 4, '你的Python爬虫教程分享一下呗', 1, '2026-08-09 14:00:00'),
(2, 4, 6, '好的，我整理一下发给你', 1, '2026-08-09 14:30:00'),
(2, 6, 4, 'Pandas那个问题解决了吗？', 0, '2026-08-09 15:20:00'),
-- 会话3: student02(5) ↔ student03(6)
(3, 5, 6, '你考研英语用的什么资料？', 1, '2026-08-08 18:00:00'),
(3, 6, 5, '主要用真题，配合田静的语法课', 1, '2026-08-08 18:30:00'),
(3, 5, 6, '考研真题我发你了，注意查收', 1, '2026-08-08 19:45:00'),
-- 会话4: student04(7) ↔ student05(8)
(4, 7, 8, '你四级听力怎么练的？能分享一下方法吗', 1, '2026-08-07 13:00:00'),
(4, 8, 7, '精听+泛听，每天坚持1.5小时', 1, '2026-08-07 13:30:00'),
(4, 7, 8, '四级听力技巧分享给你了', 1, '2026-08-07 14:10:00');


-- ================================================================
-- 补充消息通知: 好友请求通知
-- ================================================================

INSERT INTO `message` (`user_id`, `sender_id`, `related_id`, `title`, `content`, `msg_type`, `is_read`) VALUES
(4, 14, 9, '收到好友请求', '高志远 想添加你为好友', 'friend_request', 0),
(5, 15, 10, '收到好友请求', '孙嘉怡 想添加你为好友', 'friend_request', 0);


-- ================================================================
-- 初始化完成
-- ================================================================
-- 验证建表结果:
-- SELECT TABLE_NAME, TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'personal_growth_platform';
--
-- 验证数据量:
-- SELECT '用户' AS 表名, COUNT(*) AS 数量 FROM user
-- UNION ALL SELECT '任务包', COUNT(*) FROM task_package
-- UNION ALL SELECT '子任务', COUNT(*) FROM task_item
-- UNION ALL SELECT '资源', COUNT(*) FROM market_resource
-- UNION ALL SELECT '成果帖子', COUNT(*) FROM achievement_post
-- UNION ALL SELECT '评论', COUNT(*) FROM achievement_comment
-- UNION ALL SELECT '打卡记录', COUNT(*) FROM check_record
-- UNION ALL SELECT '自习房间', COUNT(*) FROM study_room
-- UNION ALL SELECT '审核记录', COUNT(*) FROM audit_log;
--
-- 完整账号列表（密码统一为 123456）:
--   管理员: admin / admin02 / admin03
--   审核员: auditor01 / auditor02 / auditor03
--   教  师: teacher01 / teacher02 / teacher03 / teacher04 / teacher05
--   学  生: student01 ~ student15
--
-- 密码哈希已通过 bcrypt 生成，可直接登录使用


-- ================================================================
-- 开始执行: seed_data.sql
-- ================================================================

-- ================================================================
-- 个人成长学习平台 —— 补充测试数据脚本
-- 执行前提: 已执行 init.sql 完成建表
-- 使用方法: Navicat 中选择 personal_growth_platform 数据库 → 新建查询 → 粘贴执行
-- ================================================================

USE personal_growth_platform;

-- ================================================================
-- 补充用户数据（原有5个 + 新增15个学生/教师 + 6个管理员/审核员/教师 = 26个用户）
-- init.sql 已插入: 1=admin, 2=auditor01, 3=teacher01, 4=student01, 5=student02
-- 下面插入 ID 6~26
-- ================================================================
INSERT INTO `user` (`username`, `password`, `role`, `nickname`, `avatar`, `real_name`, `teacher_no`, `cert_status`, `status`) VALUES
('student03', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '陈思雨', NULL, NULL, NULL, 'none', 1),
('student04', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '林浩然', NULL, NULL, NULL, 'none', 1),
('student05', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '周明月', NULL, NULL, NULL, 'none', 1),
('student06', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '吴子轩', NULL, NULL, NULL, 'none', 1),
('student07', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '郑悦琳', NULL, NULL, NULL, 'none', 1),
('student08', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '王梓涵', NULL, NULL, NULL, 'none', 1),
('student09', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '刘佳怡', NULL, NULL, NULL, 'none', 1),
('student10', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '黄宇翔', NULL, NULL, NULL, 'none', 1),
('student11', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '徐梦瑶', NULL, NULL, NULL, 'none', 1),
('student12', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '何俊杰', NULL, NULL, NULL, 'none', 1),
('student13', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '罗雨萱', NULL, NULL, NULL, 'none', 1),
('student14', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '高志远', NULL, NULL, NULL, 'none', 1),
('student15', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'student', '孙嘉怡', NULL, NULL, NULL, 'none', 1),
('teacher02', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher', '李教授', NULL, '李建国', 'T20180012', 'approved', 1),
('teacher03', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher', '张老师', NULL, '张丽华', 'T20190025', 'pending', 1),
-- ↓↓↓ 新增: 管理员×2、审核员×2、教师×2 (ID 21~26) ↓↓↓
('admin02', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'admin', '系统管理员02', NULL, NULL, NULL, 'approved', 1),
('admin03', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'admin', '系统管理员03', NULL, NULL, NULL, 'approved', 1),
('auditor02', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'auditor', '审核员02', NULL, NULL, NULL, 'approved', 1),
('auditor03', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'auditor', '审核员03', NULL, NULL, NULL, 'approved', 1),
('teacher04', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher', '赵教授', NULL, '赵明阳', 'T20200008', 'approved', 1),
('teacher05', '$2b$12$C05SFrAjHDzXKyXtk3/QY.LaUwbfoge3R9VJeSrqNd.qkLN/NuqEy', 'teacher', '钱老师', NULL, '钱秀英', 'T20210030', 'approved', 1);

-- ================================================================
-- 补充任务包数据（原有2个 + 新增12个 = 14个任务包）
-- 用户ID参考: 3=teacher01, 4=student01, 19=teacher02, 25=teacher04, 26=teacher05
-- ================================================================
INSERT INTO `task_package` (`title`, `category`, `source`, `publisher_id`, `description`, `daily_hours`, `level`, `is_official`, `audit_status`) VALUES
('英语四级30天冲刺计划', '考证', 'ai_generated', 4, '针对英语四级考试的30天冲刺学习计划，覆盖听力、阅读、写作、翻译四大模块', 3, 'intermediate', 0, 'approved'),
('高等数学微积分入门到精通', '专业课', 'ai_generated', 5, '从极限到积分，系统学习微积分核心概念与计算技巧', 4, 'beginner', 0, 'approved'),
('Java后端开发工程师成长路线', '技能学习', 'ai_generated', 6, 'Java基础到Spring Boot框架，后端开发全栈技能学习计划', 3, 'intermediate', 0, 'approved'),
('考研英语真题精刷计划', '考研', 'user_published', 4, '近10年考研英语真题逐套精讲精练，配套解析笔记', 2, 'advanced', 0, 'approved'),
('Python机器学习实战30天', '技能学习', 'ai_generated', 8, 'Scikit-learn、TensorFlow入门，动手实现经典机器学习项目', 3, 'advanced', 0, 'approved'),
('大学英语语法系统精讲', '专业课', 'user_published', 19, '从词法到句法，系统梳理英语语法核心知识点，配套练习题', 2, 'beginner', 1, 'approved'),
('数据结构算法面试突击', '技能学习', 'ai_generated', 9, '链表、树、图、排序、动态规划，面试常考算法精讲精练', 4, 'intermediate', 0, 'approved'),
('考研数学线性代数全程', '考研', 'user_published', 5, '行列式、矩阵、向量组、线性方程组、特征值与特征向量', 3, 'intermediate', 0, 'approved'),
('前端Vue3从入门到实战', '技能学习', 'ai_generated', 10, 'Vue3组合式API、Vue Router、Pinia状态管理、Element Plus实战', 3, 'beginner', 0, 'approved'),
('教师资格证教育知识速记', '考证', 'ai_generated', 11, '教育学、心理学核心考点速记，配套真题模拟练习', 2, 'beginner', 0, 'pending'),
-- ↓↓↓ 新增: teacher04(25)、teacher05(26) 发布的官方任务包 ↓↓↓
('计算机网络原理系统学习', '专业课', 'user_published', 25, '从物理层到应用层，系统讲解计算机网络OSI七层模型与TCP/IP协议栈', 3, 'intermediate', 1, 'approved'),
('大学英语学术写作入门', '专业课', 'user_published', 26, '学术论文结构、引用规范、常用句型，提升英语学术写作能力', 2, 'intermediate', 1, 'approved');

-- ================================================================
-- 补充子任务数据（为新增任务包添加子任务）
-- 任务包ID: 3-14
-- ================================================================
INSERT INTO `task_item` (`package_id`, `name`, `description`, `sort_order`, `estimated_hours`) VALUES
-- 任务包3: 英语四级30天冲刺
(3, '四级听力短对话专项训练', '掌握短对话常见场景词汇，练习抓取关键信息', 1, 2.0),
(3, '四级听力长对话与短文', '训练长对话和短文听力的笔记技巧', 2, 3.0),
(3, '四级阅读仔细阅读精练', '掌握仔细阅读题型解题步骤，提高准确率', 3, 2.5),
(3, '四级阅读快速阅读技巧', '训练快速定位信息、略读扫读能力', 4, 2.0),
(3, '四级写作模板与范文背诵', '积累写作模板，背诵高分范文10篇', 5, 3.0),
(3, '四级翻译专项突破', '掌握汉译英常见句型与翻译技巧', 6, 2.0),
(3, '四级全真模拟测试', '完成5套全真模拟题，查漏补缺', 7, 5.0),
-- 任务包4: 高等数学微积分
(4, '极限的概念与计算', '理解极限定义，掌握极限计算方法', 1, 3.0),
(4, '连续性与间断点', '掌握函数连续性判定与间断点分类', 2, 2.0),
(4, '导数与微分', '理解导数几何意义，掌握求导法则', 3, 4.0),
(4, '微分中值定理', '理解罗尔定理、拉格朗日中值定理', 4, 3.0),
(4, '不定积分计算', '掌握换元法、分部积分法', 5, 4.0),
(4, '定积分及应用', '掌握定积分计算与几何应用', 6, 4.0),
-- 任务包5: Java后端开发
(5, 'Java基础语法复习', '变量、控制流、数组、方法', 1, 3.0),
(5, '面向对象编程OOP', '类与对象、继承、多态、接口', 2, 5.0),
(5, '集合框架', 'List、Set、Map的使用与原理', 3, 4.0),
(5, '多线程与并发', '线程创建、同步、线程池', 4, 5.0),
(5, 'MySQL与JDBC', '数据库连接、CRUD操作、连接池', 5, 3.0),
(5, 'Spring Boot框架入门', 'IoC、AOP、RESTful API开发', 6, 6.0),
-- 任务包6: 考研英语真题精刷
(6, '2015年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 1, 4.0),
(6, '2016年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 2, 4.0),
(6, '2017年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 3, 4.0),
(6, '2018年考研英语真题精讲', '完形、阅读、翻译、写作逐题解析', 4, 4.0),
(6, '高频词汇专项突破', '考研核心词汇3000精讲', 5, 6.0),
-- 任务包7: Python机器学习
(7, 'NumPy科学计算基础', '数组操作、线性代数、随机数', 1, 3.0),
(7, 'Pandas数据分析', 'DataFrame操作、数据清洗、分组聚合', 2, 4.0),
(7, 'Matplotlib数据可视化', '折线图、散点图、热力图绘制', 3, 2.0),
(7, 'Scikit-learn线性回归', '简单线性回归、多元线性回归实战', 4, 4.0),
(7, '逻辑回归与分类', '二分类、多分类、模型评估', 5, 4.0),
(7, '决策树与随机森林', '决策树原理、随机森林集成学习', 6, 4.0),
(7, '神经网络入门', 'TensorFlow/Keras搭建简单神经网络', 7, 5.0),
-- 任务包8: 数据结构算法面试
(8, '数组与链表', '动态数组、单链表、双链表操作', 1, 3.0),
(8, '栈与队列', '栈的应用、队列的实现、单调栈', 2, 3.0),
(8, '二叉树遍历', '前序、中序、后序、层序遍历', 3, 3.0),
(8, '排序算法', '快排、归并、堆排序及复杂度分析', 4, 4.0),
(8, '二分查找', '二分查找变体、旋转数组查找', 5, 2.0),
(8, '动态规划入门', '背包问题、最长子序列、路径问题', 6, 5.0),
(8, '图论基础', 'BFS、DFS、最短路径、拓扑排序', 7, 5.0),
-- 任务包9: 考研数学线性代数
(9, '行列式计算', '行列式性质、展开定理、克莱默法则', 1, 3.0),
(9, '矩阵运算', '矩阵乘法、逆矩阵、秩', 2, 4.0),
(9, '向量组线性相关性', '线性组合、线性相关与无关、极大无关组', 3, 4.0),
(9, '线性方程组', '齐次/非齐次方程组解的结构', 4, 4.0),
(9, '特征值与特征向量', '特征值求解、相似矩阵、对角化', 5, 5.0),
-- 任务包10: 前端Vue3
(10, 'HTML/CSS/JS基础回顾', '前端三件套核心知识快速复习', 1, 3.0),
(10, 'Vue3组合式API', 'setup、ref、reactive、computed', 2, 4.0),
(10, 'Vue Router路由管理', '路由配置、嵌套路由、导航守卫', 3, 3.0),
(10, 'Pinia状态管理', 'store定义、状态读写、actions', 4, 3.0),
(10, 'Element Plus组件库', '表单、表格、弹窗、分页组件使用', 5, 4.0),
(10, 'Vue3项目实战', '从零搭建一个完整后台管理系统', 6, 6.0),
-- 任务包13: 计算机网络原理系统学习 (teacher04)
(13, '计算机网络概述', '了解计算机网络发展历程、分类、性能指标', 1, 2.0),
(13, '物理层基础', '数据通信基础、信道复用技术、物理层设备', 2, 3.0),
(13, '数据链路层', 'MAC协议、CSMA/CD、交换机工作原理', 3, 4.0),
(13, '网络层与IP协议', 'IP地址、子网划分、路由算法、ICMP', 4, 5.0),
(13, '传输层TCP/UDP', 'TCP三次握手、流量控制、拥塞控制', 5, 5.0),
(13, '应用层协议', 'HTTP、DNS、SMTP、FTP协议详解', 6, 4.0),
-- 任务包14: 大学英语学术写作入门 (teacher05)
(14, '学术论文结构', 'IMRD结构：引言、方法、结果、讨论', 1, 2.0),
(14, '引用规范与格式', 'APA、MLA、Chicago引用格式详解', 2, 3.0),
(14, '学术写作常用句型', '引言、方法、结果、讨论各部分高频句型', 3, 3.0),
(14, '摘要写作技巧', '摘要的结构要素与写作规范', 4, 2.0),
(14, '学术写作实战练习', '完成一篇完整的学术小论文', 5, 6.0);

-- ================================================================
-- 补充资源集市数据（原有2个 + 新增15个 = 17个资源）
-- ================================================================
INSERT INTO `market_resource` (`title`, `category`, `content`, `publisher_id`, `publisher_role`, `is_teacher_certified`, `audit_status`, `view_count`) VALUES
('英语四级高频词汇1800整理版', '考证', '# 四级高频词汇1800\n\n## A开头\n- abandon v.放弃\n- ability n.能力\n- abroad adv.在国外\n\n## B开头\n- background n.背景\n- balance n.平衡\n\n（完整版见附件）', 4, 'student', 0, 'approved', 156),
('微积分公式大全（手写笔记）', '专业课', '# 微积分公式汇总\n\n## 导数公式\n- (sinx)\' = cosx\n- (cosx)\' = -sinx\n- (e^x)\' = e^x\n- (lnx)\' = 1/x\n\n## 积分公式\n- ∫cosx dx = sinx + C\n- ∫sinx dx = -cosx + C', 5, 'student', 0, 'approved', 203),
('Java面试题100道精选', '技能学习', '# Java面试高频100题\n\n## 基础篇\n1. ==和equals的区别\n2. String为什么不可变\n3. HashMap底层原理\n\n## 并发篇\n4. synchronized和Lock区别\n5. volatile关键字原理', 6, 'student', 0, 'approved', 389),
('考研政治思修法基思维导图', '考研', '# 思想道德修养与法律基础\n\n## 绪论\n- 思想道德与法律的关系\n\n## 理想信念篇\n- 理想的分类\n- 信念的特征\n- 理想信念的作用', 5, 'student', 0, 'approved', 98),
('Python爬虫入门到精通教程', '技能学习', '# Python爬虫教程\n\n## 第一章 爬虫基础\n- HTTP/HTTPS协议\n- requests库入门\n\n## 第二章 数据解析\n- BeautifulSoup\n- XPath\n- 正则表达式', 8, 'student', 0, 'approved', 267),
('大学英语四级听力技巧总结', '考证', '# 四级听力技巧\n\n## 短对话\n1. 听关键词：but, however, instead\n2. 注意语气转折\n3. 场景词汇积累\n\n## 长对话\n1. 预读选项\n2. 边听边记\n3. 重点关注首尾', 4, 'student', 0, 'approved', 178),
('Spring Boot项目实战源码', '技能学习', '# Spring Boot实战项目\n\n## 项目介绍\n基于Spring Boot + MyBatis + MySQL的后台管理系统\n\n## 技术栈\n- Spring Boot 2.7\n- MyBatis Plus\n- MySQL 8.0\n- JWT鉴权', 9, 'student', 0, 'approved', 312),
('数据结构考研复习笔记', '专业课', '# 数据结构复习笔记\n\n## 第一章 绪论\n- 时间复杂度分析\n- 空间复杂度分析\n\n## 第二章 线性表\n- 顺序表\n- 链表\n- 栈和队列', 10, 'student', 0, 'approved', 145),
('前端Vue3学习路线图2026版', '技能学习', '# Vue3学习路线\n\n## 第一阶段 基础\n- HTML/CSS/JavaScript\n- ES6+语法\n\n## 第二阶段 Vue3\n- 组合式API\n- 组件通信\n- 生命周期', 10, 'student', 0, 'approved', 198),
('考研英语长难句解析100句', '考研', '# 考研长难句100句\n\n## 第1句\nThe OECD estimates that in the 27 developed economies, the average unemployment rate will reach 10% by 2014.\n\n**解析**：\n- 主干：The OECD estimates that...\n- that引导宾语从句', 4, 'student', 0, 'approved', 234),
('教师资格证教育学重点笔记', '考证', '# 教育学重点\n\n## 第一章 教育与教育学\n- 教育的概念\n- 教育的起源\n- 教育学的发展\n\n## 第二章 教育目的\n- 教育目的的概念\n- 个人本位论与社会本位论', 11, 'student', 0, 'approved', 87),
('高等数学期末复习题含答案', '专业课', '# 高数期末复习题\n\n## 一、选择题\n1. 设f(x)=x^2，则f\'(2)=？\nA. 2  B. 4  C. 8  D. 0\n\n**答案：B**\n\n2. 下列哪个函数在x=0处连续？\nA. 1/x  B. sin(1/x)  C. |x|  D. ln(x)', 14, 'student', 0, 'approved', 256),
('机器学习算法对比总结表', '技能学习', '# 机器学习算法对比\n\n| 算法 | 类型 | 优点 | 缺点 | 适用场景 |\n|------|------|------|------|----------|\n| 线性回归 | 监督 | 简单快速 | 欠拟合 | 连续值预测 |\n| 决策树 | 监督 | 可解释 | 过拟合 | 分类 |\n| KNN | 监督 | 无需训练 | 计算量大 | 分类回归 |', 8, 'student', 0, 'pending', 0),
-- ↓↓↓ 新增: teacher04(25)、teacher05(26) 发布的认证资源 ↓↓↓
('计算机网络OSI七层模型详解', '专业课', '# OSI七层模型详解\n\n## 物理层\n- 传输比特流\n- 关注信号编码、传输介质\n\n## 数据链路层\n- MAC地址寻址\n- CSMA/CD协议\n- 交换机工作原理\n\n## 网络层\n- IP协议\n- 路由选择\n- ICMP协议\n\n## 传输层\n- TCP三次握手\n- UDP无连接\n\n## 应用层\n- HTTP/HTTPS\n- DNS\n- SMTP/FTP', 25, 'teacher', 1, 'approved', 178),
('英语学术写作常用句型100例', '专业课', '# 学术写作高频句型\n\n## 引言部分\n1. This paper aims to investigate...\n2. Recent studies have shown that...\n3. However, little attention has been paid to...\n\n## 方法部分\n1. The experiment was conducted using...\n2. Data were collected from...\n3. Statistical analysis was performed using...\n\n## 结果部分\n1. The results indicate that...\n2. As shown in Figure 1...\n3. There was a significant difference between...\n\n## 讨论部分\n1. These findings suggest that...\n2. This is consistent with previous research...\n3. One limitation of this study is...', 26, 'teacher', 1, 'approved', 145);

-- ================================================================
-- 补充成果帖子数据（原有2个 + 新增15个 = 17个帖子）
-- 用户ID: 4=student01, 5=student02, 6=student03 ... 15=student12, 19=teacher02, 25=teacher04, 26=teacher05
-- ================================================================
INSERT INTO `achievement_post` (`user_id`, `content`, `like_count`, `comment_count`, `audit_status`) VALUES
(4, '坚持打卡第7天！今天完成了Python数据分析的Pandas模块学习，整理了DataFrame操作的速查表分享给大家，常用操作一目了然！', 32, 5, 'approved'),
(5, '考研倒计时90天！今天做了2018年考研英语真题，阅读理解错了4个，感觉还需加强长难句分析能力，分享一下今天的笔记', 18, 3, 'approved'),
(6, 'Java多线程学完了！用synchronized和ReentrantLock分别实现了线程安全的单例模式，对比了两种方式的性能差异，发现Lock效率更高', 45, 8, 'approved'),
(7, '英语四级听力从120分提升到180分的方法：每天精听30分钟+泛听1小时，坚持一个月效果显著！分享我的听力训练计划表', 67, 12, 'approved'),
(8, '用Scikit-learn完成了第一个机器学习项目——波士顿房价预测！线性回归模型R2达到0.73，虽然不算高但很有成就感，附上代码和思路', 89, 15, 'approved'),
(9, '数据结构算法刷完了LeetCode前100题！总结一下高频考点：二叉树遍历、动态规划、BFS/DFS。分享我的刷题笔记和解题模板', 56, 9, 'approved'),
(10, 'Vue3项目上线了！用Vue3+Element Plus做了一个后台管理系统，包含登录鉴权、表格CRUD、权限管理。源码已开源，欢迎交流', 73, 11, 'approved'),
(11, '教师资格证笔试一次过！教育知识与能力87分，分享我的备考经验：重点背诵教育学原理和心理学概念，配合真题模拟', 41, 6, 'approved'),
(12, '高数微积分期末考了92分！分享一下我的学习方法：上课认真听讲+课后及时复习+大量刷题。微积分的关键是理解极限思想', 38, 7, 'approved'),
(13, '今天用Python爬虫抓取了豆瓣Top250电影数据，做了数据清洗和可视化分析，发现了评分分布的一些有趣规律，附上分析报告', 52, 8, 'approved'),
(14, '线性代数矩阵运算总结：行列式、逆矩阵、秩的求解方法整理成思维导图了，考前复习效率翻倍！', 29, 4, 'approved'),
(15, '前端面试复盘：今天面试了某互联网公司，问了Vue3组合式API原理、虚拟DOM diff算法、前端性能优化方案，分享我的回答思路', 64, 10, 'approved'),
(4, '考研政治马原部分学完了！唯物论、辩证法、认识论三大板块的思维导图整理完毕。发现用框架图记忆比死记硬背效率高太多', 35, 5, 'approved'),
-- ↓↓↓ 新增: teacher04(25)、teacher05(26) 的成果帖 ↓↓↓
(25, '期末复习资料整理完毕！计算机网络各章节重点知识思维导图已上传，涵盖OSI七层模型、TCP/IP协议栈、路由算法等核心考点，希望对同学们的复习有帮助', 52, 7, 'approved'),
(26, '学术写作课程结课了！整理了一份英语学术论文写作全流程指南，从选题、文献综述到引用格式，帮助大家规避常见的写作误区', 38, 5, 'approved');

-- ================================================================
-- 补充评论数据
-- ================================================================
INSERT INTO `achievement_comment` (`post_id`, `user_id`, `content`, `is_teacher`) VALUES
(3, 5, 'DataFrame速查表太实用了，正需要这个！', 0),
(3, 19, '整理得很系统，建议补充merge和concat的区别说明，这是面试常考点。', 1),
(3, 8, '感谢分享！收藏了', 0),
(4, 4, '阅读理解确实需要加强长难句分析，推荐田静老师的语法课', 0),
(4, 6, '同考研党，一起加油！你的笔记很有参考价值', 0),
(5, 10, 'ReentrantLock确实比synchronized灵活，但要注意手动释放锁', 0),
(5, 4, '请问性能差异具体是多少？有测试数据吗？', 0),
(5, 19, '补充一点：synchronized是JVM层面，ReentrantLock是API层面，使用场景有区别。总结得不错。', 1),
(6, 8, '精听+泛听的组合方法很科学，我也用这个方法提升了不少', 0),
(6, 11, '听力训练计划表能分享一下吗？谢谢', 0),
(7, 6, '波士顿房价预测是经典项目！可以试试特征工程提升R2', 0),
(7, 9, '代码能开源吗？想学习一下你的实现思路', 0),
(7, 19, 'R2=0.73作为入门项目不错，可以尝试加入正则化或使用随机森林对比效果。', 1),
(7, 5, '机器学习入门最佳项目之一！', 0),
(8, 4, 'LeetCode前100题含金量很高，感谢分享笔记', 0),
(8, 7, '动态规划确实是最难的，你的解题模板很实用', 0),
(9, 6, '源码地址求分享！想学习你的项目结构', 0),
(9, 10, 'Vue3+Element Plus确实是后台管理系统的最佳实践', 0),
(10, 11, '教资笔记求分享！我也在备考', 0),
(11, 5, '92分太强了！微积分确实需要大量刷题', 0),
(12, 8, '豆瓣爬虫分析很有趣，可视化部分用的什么库？', 0),
(13, 14, '思维导图方式记忆确实高效！', 0),
(14, 10, '前端面试题总结得很全面，收藏了', 0),
(14, 6, '虚拟DOM diff算法是面试必考，了解key的作用很关键', 0),
(15, 5, '框架图记忆法确实比死记硬背好太多，感谢分享', 0),
-- ↓↓↓ 新增: 帖子16(teacher04)、17(teacher05) 的评论 ↓↓↓
(16, 6, 'OSI七层模型思维导图太清晰了！期末复习救星', 0),
(16, 9, '路由算法部分讲得很透彻，感谢赵教授分享', 0),
(16, 26, '补充一点：建议同学们重点关注TCP三次握手和四次挥手，这是面试和考试的高频考点', 1),
(16, 8, '正好在复习计算机网络，这份资料太及时了', 0),
(17, 4, '学术写作指南非常实用，引用格式部分解决了我的大问题', 0),
(17, 11, '请问有完整的APA引用示例吗？', 0),
(17, 25, '写作流程图很清晰，建议增加文献管理工具的使用教程', 1),
(17, 7, '学术写作一直是我的弱项，这份指南帮大忙了', 0);

-- ================================================================
-- 补充点赞数据
-- ================================================================
INSERT INTO `achievement_like` (`post_id`, `user_id`) VALUES
(3, 5), (3, 6), (3, 7), (3, 8), (3, 19),
(4, 4), (4, 6), (4, 10),
(5, 4), (5, 7), (5, 9), (5, 10),
(6, 4), (6, 5), (6, 8), (6, 9), (6, 11),
(7, 5), (7, 6), (7, 9), (7, 10), (7, 12), (7, 13),
(8, 4), (8, 6), (8, 7), (8, 10), (8, 11),
(9, 5), (9, 8), (9, 10), (9, 13),
(10, 4), (10, 6), (10, 11),
(11, 5), (11, 8), (11, 14),
(12, 6), (12, 7), (12, 9), (12, 10),
(13, 4), (13, 5), (13, 14),
(14, 5), (14, 8), (14, 10), (14, 11),
(15, 5), (15, 6), (15, 7),
-- ↓↓↓ 新增: 帖子16、17 的点赞 ↓↓↓
(16, 4), (16, 5), (16, 6), (16, 7), (16, 8), (16, 9), (16, 10),
(17, 4), (17, 5), (17, 6), (17, 11), (17, 12);

-- ================================================================
-- 补充打卡记录数据（模拟近7天打卡）
-- ================================================================
INSERT INTO `check_record` (`user_id`, `task_id`, `status`, `remark`, `check_time`) VALUES
-- student01 打卡记录 (task_id 1-5 属于任务包1)
(4, 1, 'completed', '环境搭建完成，Python基础语法过完了一遍', '2026-08-05 10:30:00'),
(4, 2, 'completed', 'NumPy数组运算学完了，广播机制还需要再理解', '2026-08-06 14:20:00'),
(4, 3, 'completed', 'Pandas数据处理实战完成，DataFrame操作熟练了', '2026-08-07 09:15:00'),
(4, 4, 'completed', 'Matplotlib可视化画了几个图表，效果不错', '2026-08-08 16:45:00'),
(4, 5, 'completed', '综合项目完成！数据分析报告写完了', '2026-08-09 20:00:00'),
-- student02 打卡记录 (task_id 6-8 属于任务包2 考研政治)
(5, 6, 'completed', '马原绪论学完，理解了马克思主义的科学内涵', '2026-08-05 11:00:00'),
(5, 7, 'completed', '唯物论部分搞定，物质与意识的辩证关系是重点', '2026-08-06 15:30:00'),
(5, 8, 'completed', '辩证法对立统一规律，矛盾分析法需要反复理解', '2026-08-07 19:00:00'),
-- student03 打卡记录 (task_id 9-15 属于任务包3 英语四级)
(6, 9, 'completed', '听力短对话训练50题，正确率提升到80%', '2026-08-06 10:00:00'),
(6, 10, 'completed', '长对话听力练习，笔记技巧很实用', '2026-08-07 14:00:00'),
(6, 11, 'completed', '仔细阅读精练8篇，掌握了定位法', '2026-08-08 16:00:00'),
-- student04 打卡记录 (task_id 16-21 属于任务包4 微积分)
(5, 16, 'completed', '极限计算方法掌握了，等价无穷小很实用', '2026-08-05 09:30:00'),
(5, 17, 'completed', '连续性和间断点分类搞清楚了', '2026-08-06 13:00:00'),
(5, 18, 'completed', '求导法则练了很多题，复合函数求导要细心', '2026-08-07 15:00:00'),
(5, 19, 'completed', '中值定理理解了，证明题还需要多练', '2026-08-08 17:30:00'),
-- student05 打卡记录 (task_id 22-27 属于任务包5 Java)
(6, 22, 'completed', 'Java基础语法复习完，跟C++对比学习效率高', '2026-08-06 10:30:00'),
(6, 23, 'completed', 'OOP四大特性理解了，多态的实际应用还需练习', '2026-08-07 14:30:00'),
(6, 24, 'completed', '集合框架源码看了ArrayList和HashMap', '2026-08-08 16:00:00');

-- ================================================================
-- 补充学习笔记数据
-- ================================================================
INSERT INTO `note` (`user_id`, `package_id`, `title`, `content`, `is_public`) VALUES
(4, 1, 'Python数据分析学习笔记', '# Python数据分析笔记\n\n## NumPy核心\n- ndarray创建：np.array(), np.zeros(), np.ones()\n- 数组索引：支持布尔索引和花式索引\n- 广播机制：不同形状数组运算规则\n\n## Pandas核心\n- DataFrame创建与索引\n- 数据清洗：dropna(), fillna()\n- 分组聚合：groupby() + agg()', 1),
(4, 1, 'Pandas速查表', '# Pandas常用操作\n\n```python\n# 读取数据\ndf = pd.read_csv("data.csv")\n\n# 查看数据\ndf.head()        # 前5行\ndf.info()        # 数据信息\ndf.describe()    # 统计描述\n\n# 数据筛选\ndf[df["age"] > 18]\ndf.query("age > 18")\n\n# 分组聚合\ndf.groupby("city")["salary"].mean()\n```', 1),
(5, 2, '考研政治马原笔记', '# 马原核心考点\n\n## 唯物论\n1. 物质决定意识，意识对物质有能动作用\n2. 物质的唯一特性是客观实在性\n\n## 辩证法\n1. 对立统一规律是唯物辩证法的实质和核心\n2. 量变和质变的辩证关系\n3. 否定之否定规律\n\n## 认识论\n1. 实践是认识的基础\n2. 真理的绝对性和相对性', 1),
(6, 3, '英语四级备考心得', '# 四级备考笔记\n\n## 听力技巧\n- 预读选项，预判话题\n- 听关键词：but, however, instead\n- 注意数字、时间、地点\n\n## 阅读技巧\n- 先看题目再看文章\n- 定位关键词\n- 仔细阅读注意同义替换', 0),
(5, 4, '微积分公式整理', '# 微积分公式大全\n\n## 基本求导公式\n- (x^n)\' = nx^(n-1)\n- (sinx)\' = cosx\n- (cosx)\' = -sinx\n- (e^x)\' = e^x\n- (lnx)\' = 1/x\n\n## 基本积分公式\n- ∫x^n dx = x^(n+1)/(n+1) + C\n- ∫1/x dx = lnx + C\n- ∫e^x dx = e^x + C\n- ∫cosx dx = sinx + C\n\n## 常用等价无穷小\n- sinx ~ x\n- tanx ~ x\n- 1-cosx ~ x^2/2', 1),
(6, 5, 'Java集合框架笔记', '# Java集合框架\n\n## List\n- ArrayList：底层数组，查询快\n- LinkedList：底层链表，增删快\n\n## Set\n- HashSet：无序，不允许重复\n- TreeSet：自动排序\n\n## Map\n- HashMap：key-value存储，允许null\n- TreeMap：按key排序\n\n## 面试常问\n- HashMap底层：数组+链表+红黑树\n- 扩容机制：初始16，负载因子0.75', 1);

-- ================================================================
-- 补充资源收藏数据
-- ================================================================
INSERT INTO `user_favorite` (`user_id`, `resource_id`) VALUES
(4, 3), (4, 5), (4, 7), (4, 9),
(5, 1), (5, 4), (5, 11),
(6, 3), (6, 7), (6, 10),
(7, 1), (7, 6), (7, 9),
(8, 5), (8, 7), (8, 13),
(9, 3), (9, 7), (9, 8),
(10, 9), (10, 10), (10, 7);

-- ================================================================
-- 补充消息通知数据
-- ================================================================
INSERT INTO `message` (`user_id`, `title`, `content`, `msg_type`, `is_read`) VALUES
(4, '审核通过', '您发布的资源《Python数据分析完整学习路线图》已审核通过，现已上线资源集市', 'audit', 1),
(4, '收到新评论', '王老师评论了你的成果《Pandas速查表分享》', 'comment', 0),
(4, '收到新点赞', '陈思雨等5人点赞了你的成果帖子', 'like', 0),
(5, '审核通过', '您发布的资源《考研政治高频考点汇总》已审核通过', 'audit', 1),
(5, '审核驳回', '您发布的资源《测试资源》因内容不完整被驳回，请补充后重新提交', 'audit', 0),
(6, '收到新评论', '林浩然评论了你的成果帖', 'comment', 0),
(7, '系统通知', '欢迎加入个人成长学习平台！完善个人信息可获得更好体验', 'system', 1),
(8, '收到新点赞', '周明月等8人点赞了你的成果帖', 'like', 0),
(9, '审核通过', '您发布的资源《Spring Boot项目实战源码》已审核通过', 'audit', 1),
(10, '收到新评论', '吴子轩评论了你的成果帖', 'comment', 0),
-- ↓↓↓ 新增: 新用户消息 ↓↓↓
(25, '资源审核通过', '您发布的资源《计算机网络OSI七层模型详解》已审核通过', 'audit', 1),
(25, '收到新评论', '钱老师评论了您的成果帖', 'comment', 0),
(26, '资源审核通过', '您发布的资源《英语学术写作常用句型100例》已审核通过', 'audit', 1),
(26, '收到新点赞', '李同学等5人点赞了您的成果帖', 'like', 0),
(23, '系统通知', '您有新的审核任务待处理，请及时查看', 'system', 0),
(24, '系统通知', '您有新的审核任务待处理，请及时查看', 'system', 0);

-- ================================================================
-- 补充结伴自习房间数据
-- ================================================================
INSERT INTO `study_room` (`name`, `creator_id`, `target_minutes`, `is_private`, `max_members`, `status`) VALUES
('考研冲刺自习室', 5, 240, 0, 20, 'active'),
('Python学习打卡群', 4, 120, 0, 15, 'active'),
('英语四级备考自习', 7, 180, 0, 10, 'active'),
('Java后端学习小组', 6, 200, 0, 12, 'active'),
('前端进阶自习室', 10, 150, 0, 8, 'active'),
('考研数学刷题营', 5, 300, 0, 15, 'active');

INSERT INTO `study_room_member` (`room_id`, `user_id`, `study_minutes`, `is_studying`) VALUES
(1, 5, 480, 0), (1, 4, 360, 0), (1, 8, 420, 0), (1, 11, 300, 0),
(2, 4, 540, 1), (2, 6, 420, 0), (2, 8, 360, 0), (2, 9, 240, 0),
(3, 7, 360, 0), (3, 11, 300, 0), (3, 13, 240, 0),
(4, 6, 600, 0), (4, 9, 480, 0), (4, 10, 360, 0),
(5, 10, 420, 0), (5, 12, 300, 0), (5, 15, 240, 0),
(6, 5, 720, 0), (6, 14, 480, 0),
-- ↓↓↓ 新增: 新教师加入自习房间 ↓↓↓
(1, 25, 360, 0),
(3, 26, 240, 0),
(6, 25, 480, 0);

-- ================================================================
-- 补充审核记录数据
-- auditor01=2, auditor02=23, auditor03=24
-- ================================================================
INSERT INTO `audit_log` (`auditor_id`, `content_id`, `content_type`, `action`, `reject_reason`) VALUES
-- auditor01 的审核记录
(2, 1, 'resource', 'approve', NULL),
(2, 2, 'resource', 'approve', NULL),
(2, 1, 'achievement', 'approve', NULL),
(2, 2, 'achievement', 'approve', NULL),
(2, 3, 'resource', 'approve', NULL),
(2, 4, 'resource', 'approve', NULL),
(2, 5, 'resource', 'approve', NULL),
(2, 6, 'resource', 'approve', NULL),
(2, 7, 'resource', 'approve', NULL),
(2, 8, 'resource', 'approve', NULL),
(2, 13, 'resource', 'reject', '内容缺少具体代码示例，请补充完整后重新提交'),
(2, 3, 'achievement', 'approve', NULL),
(2, 4, 'achievement', 'approve', NULL),
(2, 5, 'achievement', 'approve', NULL),
-- ↓↓↓ 新增: auditor02(23) 的审核记录 ↓↓↓
(23, 9, 'resource', 'approve', NULL),
(23, 10, 'resource', 'approve', NULL),
(23, 11, 'resource', 'approve', NULL),
(23, 12, 'resource', 'approve', NULL),
(23, 6, 'achievement', 'approve', NULL),
(23, 7, 'achievement', 'approve', NULL),
(23, 14, 'resource', 'reject', '资源内容排版不规范，请使用标准Markdown格式重新编辑后提交'),
-- ↓↓↓ 新增: auditor03(24) 的审核记录 ↓↓↓
(24, 14, 'resource', 'approve', NULL),
(24, 15, 'resource', 'approve', NULL),
(24, 16, 'resource', 'approve', NULL),
(24, 17, 'resource', 'approve', NULL),
(24, 8, 'achievement', 'approve', NULL),
(24, 9, 'achievement', 'approve', NULL),
(24, 16, 'achievement', 'approve', NULL),
(24, 17, 'achievement', 'approve', NULL);

-- ================================================================
-- 数据统计
-- ================================================================
-- 执行后数据量:
--   user表:              26条 (3管理员 + 3审核员 + 5教师 + 15学生)
--   task_package表:      14条 (覆盖5大分类，含教师官方认证)
--   task_item表:         60条 (每个任务包含5-7个子任务)
--   market_resource表:   17条 (14已通过 + 1待审核 + 2原有，含教师认证资源)
--   check_record表:      18条 (模拟近7天打卡)
--   note表:               6条 (含公开和私有)
--   achievement_post表:  17条 (全部审核通过，含教师成果)
--   achievement_comment:  33条 (含教师专业点评)
--   achievement_like:     63条
--   user_favorite:       22条
--   message:             16条
--   study_room:           6个房间
--   study_room_member:   22条成员记录
--   audit_log:           29条审核记录 (3位审核员均有记录)
--
-- 完整账号列表（密码统一为 123456）:
--   管理员: admin / admin02 / admin03
--   审核员: auditor01 / auditor02 / auditor03
--   教  师: teacher01 / teacher02 / teacher03 / teacher04 / teacher05
--   学  生: student01 ~ student15


-- ================================================================
-- 开始执行: migrate_v6.sql
-- ================================================================

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


-- ================================================================
-- 开始执行: migrate_v7.sql
-- ================================================================

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


-- ================================================================
-- 开始执行: migrate_v8.sql
-- ================================================================

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


-- ================================================================
-- 开始执行: migrate_study_room_message.sql
-- ================================================================

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


-- ================================================================
-- 开始执行: fix_database.sql
-- ================================================================

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


