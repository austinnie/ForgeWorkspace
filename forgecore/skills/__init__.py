# forgecore/skills/__init__.py
"""
forgecore.skills - 全局技能库
用法:
    from forgecore.skills import SkillManager, skill_manager
    result = skill_manager.run("image_curator", directory="output/daily")
"""
from .base import BaseSkill
from .manager import SkillManager, skill_manager

__all__ = ["BaseSkill", "SkillManager", "skill_manager"]