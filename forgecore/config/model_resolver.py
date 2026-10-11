# forgecore/config/model_resolver.py
"""模型路径解析工具（跨 app 通用）"""

from typing import Optional

from forgecore.config.registry import ModelRegistry


def resolve_model_path(model_name: str) -> Optional[str]:
    """
    按模型名找绝对路径。先扫 sd15，再扫 sdxl。
    找不到返回 None。
    """
    if not model_name:
        return None
    for m_type in ("sd15", "sdxl"):
        for m in ModelRegistry.scan_checkpoints(m_type):
            if m.get("name") == model_name:
                return m.get("absolute_path")
    return None


def resolve_model(model_name: str) -> Optional[dict]:
    """
    按模型名找完整信息（含 size_mb / type）。
    找不到返回 None。
    """
    if not model_name:
        return None
    for m_type in ("sd15", "sdxl"):
        for m in ModelRegistry.scan_checkpoints(m_type):
            if m.get("name") == model_name:
                return m
    return None