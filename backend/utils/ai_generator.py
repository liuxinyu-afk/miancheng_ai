"""
AI 学习任务包生成工具
对接豆包/通义千问/智谱GLM 等大模型接口，将学习目标拆解为结构化子任务
"""
import json
import logging
from typing import Any

import requests

from config import settings

logger = logging.getLogger(__name__)


def generate_study_tasks(
    goal: str,
    daily_hours: int,
    level: str,
    category: str | None = None,
    deadline_days: int | None = None,
    learning_style: str | None = None,
    focus_points: str | None = None,
) -> dict[str, Any]:
    """
    调用大模型 API，根据学习目标生成结构化学习计划

    :param goal: 学习目标，如 "Python数据分析入门"
    :param daily_hours: 每日学习时长（小时）
    :param level: 基础水平 beginner/intermediate/advanced
    :param category: 学习领域分类
    :param deadline_days: 目标完成天数
    :param learning_style: 学习风格偏好
    :param focus_points: 特别关注点
    :return: {"overview": {...}, "tasks": [...]}
    """
    level_map = {
        "beginner": "零基础/初学者",
        "intermediate": "有一定基础，希望进阶提升",
        "advanced": "基础扎实，追求高级应用",
    }
    level_desc = level_map.get(level, "初学者")

    style_map = {
        "theory": "偏重理论理解，先吃透原理再动手",
        "practice": "偏重实践练习，边做边学",
        "project": "以项目驱动，通过完整项目学习",
        "mixed": "理论与实践结合，交替进行",
    }
    style_desc = style_map.get(learning_style, "理论与实践结合") if learning_style else "理论与实践结合"

    # 构建详细提示词
    extra_info = ""
    if category:
        extra_info += f"\n学习领域：{category}"
    if deadline_days:
        total_hours = deadline_days * daily_hours
        extra_info += f"\n目标周期：{deadline_days}天（总可用约{total_hours}小时）"
    if focus_points:
        extra_info += f"\n特别关注：{focus_points}"

    style_instruction = (
        "更多动手实践环节" if learning_style == "practice"
        else "更多项目案例" if learning_style == "project"
        else "更多理论深挖" if learning_style == "theory"
        else "理论与实践交替"
    )

    prompt = f"""你是一位资深学习规划师。请根据以下信息，制定一个详细、结构化、分阶段的学习计划。

学习目标：{goal}
每日学习时长：{daily_hours}小时
学习者基础：{level_desc}
学习风格偏好：{style_desc}{extra_info}

要求：
1. 将学习目标拆解为 8-15 个递进式子任务，分为3-4个阶段（如：基础阶段、进阶阶段、实战阶段、总结阶段）
2. 每个子任务包含：
   - name：任务名称（简洁明了）
   - description：任务描述（具体可执行，包含学习要点、建议方法和实践方向，100-200字）
   - estimated_hours：预计学习时长（小时）
   - phase：所属阶段名称
   - objectives：学习目标列表（2-3个，该任务完成后应掌握的能力）
   - resources：推荐学习资源列表（2-3个，如书籍、网站、工具、项目等）
3. 按学习顺序排列，从基础到进阶
4. 根据学习风格偏好调整任务设计：{style_instruction}
5. 如果有目标周期，合理分配总时长到各子任务

请严格以以下JSON格式输出，不要包含任何其他文字：
{{
  "overview": {{
    "summary": "用2-3句话概述整个学习计划的思路和预期效果",
    "total_hours": 80,
    "estimated_days": 20,
    "phases": ["阶段1名称", "阶段2名称", "阶段3名称"]
  }},
  "tasks": [
    {{
      "name": "任务名称",
      "description": "任务描述（包含具体学习内容和实践建议）",
      "estimated_hours": 2.5,
      "phase": "阶段名称",
      "objectives": ["目标1", "目标2"],
      "resources": ["资源1", "资源2"]
    }}
  ]
}}"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.AI_API_KEY}",
    }
    payload: dict[str, Any] = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": "你是一位专业的学习规划师，擅长制定结构化、分阶段的学习计划。你总是以标准JSON格式输出结果。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    try:
        resp = requests.post(
            settings.AI_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()

        content = result["choices"][0]["message"]["content"]

        # 提取 JSON 内容（模型可能返回带 markdown 包裹的 JSON）
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content
            content = content.rsplit("```", 1)[0]
            content = content.strip()

        data = json.loads(content)

        # 标准化输出格式
        if isinstance(data, list):
            # 兼容旧格式：纯任务列表
            tasks = data
            overview = _build_overview(tasks, daily_hours, deadline_days)
        elif isinstance(data, dict) and "tasks" in data:
            tasks = data["tasks"]
            overview = data.get("overview", _build_overview(tasks, daily_hours, deadline_days))
        else:
            tasks = [data] if isinstance(data, dict) else []
            overview = _build_overview(tasks, daily_hours, deadline_days)

        # 确保每个任务都有必要字段
        for i, t in enumerate(tasks):
            t.setdefault("name", f"任务 {i + 1}")
            t.setdefault("description", "")
            t.setdefault("estimated_hours", float(daily_hours))
            t.setdefault("phase", "学习任务")
            t.setdefault("objectives", [])
            t.setdefault("resources", [])
            # 确保 estimated_hours 是数值
            try:
                t["estimated_hours"] = float(t["estimated_hours"])
            except (TypeError, ValueError):
                t["estimated_hours"] = float(daily_hours)

        return {"overview": overview, "tasks": tasks}

    except requests.RequestException as e:
        logger.error(f"AI 接口请求失败: {e}")
        return _fallback_plan(goal, daily_hours, level_desc, deadline_days)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"AI 返回解析失败: {e}")
        return _fallback_plan(goal, daily_hours, level_desc, deadline_days)


def _build_overview(tasks: list[dict], daily_hours: int, deadline_days: int | None) -> dict:
    """从任务列表构建概览信息"""
    total_hours = sum(float(t.get("estimated_hours", 0)) for t in tasks)
    phases = []
    for t in tasks:
        phase = t.get("phase", "学习任务")
        if phase not in phases:
            phases.append(phase)
    estimated_days = deadline_days or (int(total_hours / daily_hours) if daily_hours > 0 else 0)
    return {
        "summary": f"共 {len(tasks)} 个子任务，预计总时长 {total_hours:.1f} 小时",
        "total_hours": round(total_hours, 1),
        "estimated_days": estimated_days,
        "phases": phases,
    }


def _fallback_plan(goal: str, daily_hours: int, level_desc: str, deadline_days: int | None) -> dict[str, Any]:
    """AI 接口不可用时的兜底计划生成"""
    tasks = [
        {
            "name": f"{goal} - 基础概念入门",
            "description": f"系统学习{goal}的基础概念和核心术语，建立整体知识框架。建议先阅读入门教程，理解基本概念后再进行简单练习。",
            "estimated_hours": float(daily_hours),
            "phase": "基础阶段",
            "objectives": [f"理解{goal}的核心概念", "掌握基本术语和知识体系"],
            "resources": ["官方文档", "入门教程视频"],
        },
        {
            "name": f"{goal} - 核心知识深入",
            "description": f"深入理解{goal}的核心知识体系，通过理论学习和实践操作相结合的方式巩固重点知识。",
            "estimated_hours": float(daily_hours * 2),
            "phase": "基础阶段",
            "objectives": [f"掌握{goal}核心知识", "能够独立完成基础练习"],
            "resources": ["教材", "在线练习平台"],
        },
        {
            "name": f"{goal} - 进阶技能提升",
            "description": f"在掌握基础知识后，学习{goal}的进阶技能和高级特性，通过案例分析加深理解。",
            "estimated_hours": float(daily_hours * 2),
            "phase": "进阶阶段",
            "objectives": ["掌握进阶技能", "理解高级特性的应用场景"],
            "resources": ["进阶教程", "技术博客"],
        },
        {
            "name": f"{goal} - 实战项目演练",
            "description": f"通过实际操作巩固{goal}知识点，完成一个小型实战项目，将所学知识应用到实际场景中。",
            "estimated_hours": float(daily_hours * 3),
            "phase": "实战阶段",
            "objectives": ["完成实战项目", "能够独立解决实际问题"],
            "resources": ["项目教程", "开源项目参考"],
        },
        {
            "name": f"{goal} - 综合复习总结",
            "description": f"回顾全部知识点，形成完整的知识体系。整理学习笔记，查漏补缺，确保关键知识点都已掌握。",
            "estimated_hours": float(daily_hours),
            "phase": "总结阶段",
            "objectives": ["形成完整知识体系", "能够清晰表达学习成果"],
            "resources": ["学习笔记", "知识图谱工具"],
        },
    ]
    overview = _build_overview(tasks, daily_hours, deadline_days)
    overview["summary"] = f"本计划为{goal}的{level_desc}学习方案，分为基础、进阶、实战、总结四个阶段，共{len(tasks)}个任务。"
    return {"overview": overview, "tasks": tasks}
