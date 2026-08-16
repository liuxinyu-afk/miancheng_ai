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
