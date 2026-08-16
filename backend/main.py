"""
绵城AI学习集市 —— FastAPI 后端入口
启动命令: uvicorn main:app --reload --host 0.0.0.0 --port 8000
接口文档: http://127.0.0.1:8000/docs (Swagger UI)
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ================================================================
# 创建 FastAPI 应用
# ================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## 绵城AI学习集市 API 文档

    大学生个性化学习任务包生成与成果展示平台

    ### 核心功能模块
    - **认证管理**: 注册、登录、JWT鉴权、教师实名认证
    - **AI任务生成**: AI智能拆解学习目标生成结构化任务包
    - **资源集市**: 学习资源发布、审核、浏览、收藏
    - **学习中心**: 任务打卡、学习笔记、进度管理
    - **成果社区**: 成果展示、点赞评论、教师专业点评
    - **结伴自习**: 线上自习房间、计时统计
    - **审核管理**: 审核员内容审核（资源/成果/任务包）
    - **系统管理**: 管理员用户管理、数据看板、统计

    ### 角色权限
    | 角色 | 说明 |
    |------|------|
    | student | 学生用户，平台核心使用者 |
    | teacher | 认证教师，具备学生全部功能+专业点评 |
    | auditor | 专职审核员，负责内容审核 |
    | admin | 超级管理员，系统运维 |
    """,
    version=settings.APP_VERSION,
)

# ================================================================
# CORS 跨域配置（允许前端 Vue3 开发服务器访问）
# ================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 允许所有来源（ngrok 公网访问需要）
    allow_credentials=False,        # allow_origins=* 时必须为 False
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# 健康检查接口（移到 /api/health，避免和前端路由冲突）
# ================================================================
@app.get("/api/health", tags=["系统"])
def health_check():
    """健康检查"""
    return {
        "code": 200,
        "message": f"{settings.APP_NAME} 服务运行中",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# ================================================================
# 头像上传接口
# ================================================================
import shutil
import uuid
from fastapi import UploadFile, File

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "avatars")
CERT_DIR = os.path.join(os.path.dirname(__file__), "uploads", "certs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CERT_DIR, exist_ok=True)

# 挂载头像静态访问路径
app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")


@app.post("/api/auth/upload-avatar", tags=["认证管理"])
async def upload_avatar(file: UploadFile = File(...)):
    """上传头像"""
    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "code": 200,
        "message": "头像上传成功",
        "data": {"avatar": f"/uploads/avatars/{filename}"}
    }


@app.post("/api/auth/upload-cert", tags=["认证管理"])
async def upload_cert(file: UploadFile = File(...)):
    """上传资格证明图片（教师资格证/就职证明/学生证）"""
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    if ext.lower() not in ("jpg", "jpeg", "png", "gif", "webp", "bmp"):
        return {"code": 400, "message": "仅支持图片格式"}
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(CERT_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "code": 200,
        "message": "上传成功",
        "data": {"url": f"/uploads/certs/{filename}"}
    }


# ================================================================
# 注册所有业务路由
# ================================================================
from api.auth import router as auth_router
from api.ai_task import router as ai_task_router
from api.market import router as market_router
from api.study import router as study_router
from api.achievement import router as achievement_router
from api.study_room import router as study_room_router
from api.audit import router as audit_router
from api.admin import router as admin_router
from api.stats import router as stats_router
from api.message import router as message_router
from api.friend import router as friend_router
from api.ai_chat import router as ai_chat_router
from api.user_profile import router as user_profile_router
from api.badge import router as badge_router
from api.study_plan import router as study_plan_router
from api.resource_request import router as resource_request_router
from api.feedback import router as feedback_router

app.include_router(auth_router)
app.include_router(ai_task_router)
app.include_router(market_router)
app.include_router(study_router)
app.include_router(achievement_router)
app.include_router(study_room_router)
app.include_router(audit_router)
app.include_router(admin_router)
app.include_router(stats_router)
app.include_router(message_router)
app.include_router(friend_router)
app.include_router(ai_chat_router)
app.include_router(user_profile_router)
app.include_router(badge_router)
app.include_router(study_plan_router)
app.include_router(resource_request_router)
app.include_router(feedback_router)


# ================================================================
# 全局异常处理
# ================================================================
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """未捕获异常的兜底处理，避免暴露内部错误细节"""
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# ================================================================
# 托管前端静态文件（dist 目录）
# 访问 cpolar 地址直接打开前端页面，无需 Netlify
# ================================================================
DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")

if os.path.isdir(DIST_DIR):
    # 挂载静态资源目录（CSS/JS/图片等）
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        """前端路由：所有非 API 请求都返回 index.html"""
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Vue Router history 模式：找不到的路径都返回 index.html
        return FileResponse(os.path.join(DIST_DIR, "index.html"))


# ================================================================
# 启动入口
# ================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.DEBUG,
    )
