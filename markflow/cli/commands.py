"""兼容层：markflow.cli.commands"""
from typing import Dict, Any


def execute_skill(skill_name: str, **kwargs) -> Dict[str, Any]:
    """
    兼容 markflow 的 execute_skill
    转发到 forgecore.skills.manager
    """
    from forgecore.skills.manager import skill_manager
    skill_manager.scan()
    return skill_manager.run(skill_name, **kwargs)