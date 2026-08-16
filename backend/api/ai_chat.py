"""AI 智能问答路由 - 学生/教师可向 AI 提问学习相关问题"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import requests
import base64
import logging

from database import get_db
from models.user import User
from models.misc import Message
from schemas.common import ResponseOK
from utils.deps import get_current_user
from config import settings

router = APIRouter(prefix="/api/ai-chat", tags=["AI智能问答"])

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    context: str | None = Field(None, max_length=500, description="上下文/背景信息")


@router.post("/ask", summary="AI 智能问答")
def ask_question(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """向 AI 提问，获取智能解答"""
    if not settings.AI_API_KEY:
        raise HTTPException(status_code=500, detail="AI 服务未配置，请联系管理员")

    # 构建系统提示词
    system_prompt = """你是「绵城AI学习助手」，一个专业的教育领域AI问答助手。
你的职责是帮助学生和教师解答学习相关问题，包括但不限于：
- 学科知识解答（编程、数学、语言、考研等）
- 学习方法建议
- 职业规划指导
- 技术问题排查

回答要求：
1. 回答要准确、清晰、有条理
2. 如果问题涉及代码，给出代码示例
3. 如果问题复杂，分步骤解答
4. 适当使用 Markdown 格式（加粗、列表、代码块等）
5. 如果不确定答案，诚实告知并建议查阅相关资料
6. 回答用中文，长度适中，不要过于冗长"""

    user_content = payload.question
    if payload.context:
        user_content = f"背景信息：{payload.context}\n\n我的问题：{payload.question}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.AI_API_KEY}",
    }
    api_payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    try:
        resp = requests.post(
            settings.AI_API_URL,
            headers=headers,
            json=api_payload,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()

        content = result["choices"][0]["message"]["content"]
        return ResponseOK(data={"answer": content, "question": payload.question})

    except requests.RequestException as e:
        logger.error(f"AI 问答接口请求失败: {e}")
        return ResponseOK(data={
            "answer": "抱歉，AI 服务暂时不可用，请稍后再试。\n\n常见原因：\n1. 网络连接问题\n2. AI 服务额度用尽\n3. 请求超时\n\n你可以尝试重新提问，或换个简单的问题试试。",
            "question": payload.question,
        })
    except (KeyError, IndexError) as e:
        logger.error(f"AI 返回解析失败: {e}")
        return ResponseOK(data={
            "answer": "AI 返回了无法解析的内容，请尝试重新提问或换个问题。",
            "question": payload.question,
        })


@router.post("/ask-image", summary="AI 图片识别问答")
async def ask_with_image(
    image: UploadFile = File(..., description="图片文件"),
    question: str = Form(default="请解答图片中的问题", description="附加问题"),
    current_user: User = Depends(get_current_user),
):
    """上传图片向 AI 提问，AI 识别图片内容并解答"""
    if not settings.AI_API_KEY:
        raise HTTPException(status_code=500, detail="AI 服务未配置，请联系管理员")

    # 读取图片并转 base64
    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 10MB")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = image.content_type or "image/jpeg"

    system_prompt = """你是「绵城AI学习助手」，一个专业的教育领域AI问答助手。
用户上传了一张图片，请仔细识别图片内容并解答。

可能的情况：
- 题目/试卷照片：请识别题目并给出详细解答步骤
- 代码截图：请分析代码功能，指出问题并给出改进建议
- 学习笔记：请补充或纠正内容
- 错误信息截图：请分析错误原因并给出解决方案
- 其他图片：请描述图片内容并回答用户的问题

回答要求：
1. 先简要描述你看到的图片内容
2. 然后针对用户的问题进行解答
3. 回答要准确、清晰、有条理
4. 适当使用 Markdown 格式
5. 回答用中文"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.AI_API_KEY}",
    }

    # 尝试使用视觉模型（如果配置了 AI_VISION_MODEL 就用它，否则用默认模型）
    vision_model = getattr(settings, "AI_VISION_MODEL", None) or settings.AI_MODEL

    api_payload = {
        "model": vision_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question or "请解答图片中的问题"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}",
                        },
                    },
                ],
            },
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    try:
        resp = requests.post(
            settings.AI_API_URL,
            headers=headers,
            json=api_payload,
            timeout=90,
        )
        resp.raise_for_status()
        result = resp.json()

        content = result["choices"][0]["message"]["content"]
        return ResponseOK(data={"answer": content, "question": question or "请解答图片中的问题"})

    except requests.RequestException as e:
        logger.error(f"AI 图片问答接口请求失败: {e}")
        return ResponseOK(data={
            "answer": "抱歉，AI 图片识别服务暂时不可用。\n\n可能原因：\n1. 当前 AI 模型不支持图片识别\n2. 网络连接问题\n3. 图片过大或格式不支持\n\n如果你使用的是纯文本模型（如 doubao-pro-32k），需要切换到支持视觉的模型（如 doubao-1.5-vision-pro-32k）才能使用拍照解答功能。",
            "question": question or "请解答图片中的问题",
        })
    except (KeyError, IndexError) as e:
        logger.error(f"AI 图片返回解析失败: {e}")
        return ResponseOK(data={
            "answer": "AI 返回了无法解析的内容，请尝试重新上传图片或换个问题。",
            "question": question or "请解答图片中的问题",
        })
