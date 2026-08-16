# 绵城AI学习集市 - FastAPI 后端

> 大学生个性化学习任务包生成与成果展示平台
> 技术栈: FastAPI + SQLAlchemy 2.0 + MySQL 8.0 + JWT

## 一、快速启动（5步搞定）

### Step 1: 安装 Python 依赖
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: 配置环境变量
```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env，填入你的 MySQL 密码和 AI API Key
```

### Step 3: 初始化数据库
```bash
# 在 DBeaver 或 MySQL 命令行中执行 init.sql
mysql -u root -p < init.sql

# 或用 DBeaver 打开 init.sql 文件，点击执行
```

### Step 4: 启动后端服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: 访问接口文档
打开浏览器访问: http://127.0.0.1:8000/docs

---

## 二、项目目录结构

```
backend/
├── main.py                  # FastAPI 入口，注册所有路由
├── config.py                # 全局配置（读取 .env）
├── database.py              # 数据库连接 & 会话管理
├── init.sql                 # MySQL 建表脚本（8核心表+6支撑表+种子数据）
├── requirements.txt         # Python 依赖清单
├── .env.example             # 环境变量模板
│
├── models/                  # SQLAlchemy ORM 模型
│   ├── user.py              # 用户表
│   ├── task_package.py      # 任务包表
│   ├── task_item.py         # 子任务表
│   ├── market_resource.py   # 资源集市表
│   ├── check_record.py      # 打卡记录表
│   ├── note.py              # 学习笔记表
│   ├── achievement.py       # 成果帖子+评论+点赞表
│   ├── audit_log.py         # 审核记录表
│   ├── study_room.py        # 自习房间+成员表
│   └── misc.py              # 收藏+消息通知表
│
├── schemas/                 # Pydantic 请求/响应模型
│   ├── common.py            # 统一响应（ResponseOK, PageResponse）
│   ├── user.py              # 用户认证 Schema
│   ├── task.py              # 任务包 Schema
│   ├── resource.py          # 资源 Schema
│   ├── study.py             # 打卡+笔记 Schema
│   ├── achievement.py       # 成果+评论 Schema
│   ├── audit.py             # 审核 Schema
│   └── study_room.py        # 自习室 Schema
│
├── api/                     # API 路由模块（8大模块，55个接口）
│   ├── auth.py              # 认证管理（注册/登录/JWT/教师认证）
│   ├── ai_task.py           # AI任务生成（调用大模型拆解学习目标）
│   ├── market.py            # 资源集市（发布/浏览/收藏）
│   ├── study.py             # 学习中心（打卡/笔记/进度）
│   ├── achievement.py       # 成果社区（发帖/点赞/评论/消息）
│   ├── study_room.py        # 结伴自习（房间/计时）
│   ├── audit.py             # 审核管理（待审核/审核操作/历史）
│   └── admin.py             # 系统管理（看板/用户/统计）
│
└── utils/                   # 工具模块
    ├── security.py          # 密码加密(bcrypt) + JWT令牌
    ├── deps.py              # FastAPI依赖注入（鉴权/角色校验）
    ├── ai_generator.py      # AI大模型接口调用
    └── init_passwords.py    # 种子数据密码生成脚本
```

---

## 三、默认测试账号

| 角色 | 账号 | 密码 | 说明 |
|------|------|------|------|
| 管理员 | admin | 123456 | 系统运维，全部权限 |
| 审核员 | auditor01 | 123456 | 内容审核 |
| 教师 | teacher01 | 123456 | 已认证，可专业点评 |
| 学生 | student01 | 123456 | 普通学生 |
| 学生 | student02 | 123456 | 普通学生 |

---

## 四、核心API接口一览

### 认证管理 `/api/auth`
| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| POST | /register | 用户注册 | 公开 |
| POST | /login | 用户登录 | 公开 |
| GET | /me | 获取当前用户 | 登录 |
| PUT | /me | 更新资料 | 登录 |
| POST | /teacher-cert | 教师认证申请 | teacher |

### AI任务生成 `/api/ai-task`
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /generate | AI生成学习子任务 |
| POST | /save | 保存任务包 |
| GET | /my-packages | 我的任务包列表 |
| GET | /packages/{id} | 任务包详情 |
| DELETE | /packages/{id} | 删除任务包 |

### 资源集市 `/api/market`
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /publish | 发布资源(提交审核) |
| GET | /list | 资源列表(分页/筛选) |
| GET | /{id} | 资源详情 |
| GET | /my-publishments | 我的发布 |
| POST | /{id}/favorite | 收藏 |
| DELETE | /{id}/favorite | 取消收藏 |
| GET | /my-favorites | 我的收藏 |

### 学习中心 `/api/study`
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /checkin | 打卡 |
| GET | /checkin/today | 今日打卡 |
| GET | /checkin/history | 打卡历史 |
| POST | /notes | 创建笔记 |
| GET | /notes | 笔记列表 |
| PUT | /notes/{id} | 更新笔记 |
| DELETE | /notes/{id} | 删除笔记 |
| GET | /progress/{package_id} | 学习进度 |

### 成果社区 `/api/achievement`
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /posts | 发布成果 |
| GET | /posts | 成果列表 |
| GET | /posts/{id} | 成果详情 |
| POST | /posts/{id}/like | 点赞/取消 |
| POST | /posts/{id}/comments | 发表评论 |
| GET | /posts/{id}/comments | 评论列表 |
| GET | /messages | 消息通知 |
| PUT | /messages/{id}/read | 标记已读 |

### 结伴自习 `/api/study-room`
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /create | 创建房间 |
| GET | /list | 公开房间列表 |
| POST | /{id}/join | 加入房间 |
| POST | /{id}/start | 开始自习 |
| POST | /{id}/stop | 结束自习 |
| GET | /{id}/members | 房间成员 |

### 审核管理 `/api/audit` (审核员/管理员)
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /pending | 待审核列表 |
| POST | /review | 审核操作 |
| GET | /history | 审核历史 |

### 系统管理 `/api/admin` (管理员)
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /dashboard | 数据看板 |
| GET | /users | 用户列表 |
| PUT | /users/{id}/status | 启用/禁用用户 |
| GET | /cert-requests | 教师认证审核 |
| PUT | /cert-requests/{id} | 审核教师认证 |
| POST | /auditors | 创建审核员 |
| GET | /stats/resources | 资源统计 |
| GET | /stats/tasks | 任务统计 |

---

## 五、AI接口配置说明

项目支持对接豆包、通义千问、智谱GLM 等主流大模型。

1. 在 `.env` 中配置 `AI_API_URL`、`AI_API_KEY`、`AI_MODEL`
2. 豆包示例: `AI_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions`
3. 通义千问示例: `AI_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
4. 未配置 AI Key 时，系统会自动使用兜底任务生成（保证功能可用）

---

## 六、前端对接说明

前端 Vue3 项目通过 Axios 调用后端接口:

```javascript
// axios 请求头携带 JWT
const token = localStorage.getItem('token')
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

// 调用示例: 登录
POST /api/auth/login
Body: { "username": "admin", "password": "123456" }
Response: { "access_token": "...", "user": {...} }

// 调用示例: AI生成任务
POST /api/ai-task/generate
Body: { "goal": "Python数据分析入门", "daily_hours": 3, "level": "beginner" }
```
