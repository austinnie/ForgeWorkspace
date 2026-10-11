# forgecore/skills/result_utils.py
"""skill_manager.run() 返回结果的通用解析工具"""

from pathlib import Path
from typing import Optional

from PIL import Image


def extract_skill_image(result: dict) -> Optional[Image.Image]:
    """
    从 skill_manager.run 的返回里取 PIL Image。
    返回 None 表示失败或无图。
    """
    if not result or result.get("status") != "success":
        return None

    data = result.get("result") or {}

    out_p = data.get("output_path") or data.get("image_path")
    if out_p and Path(out_p).exists():
        try:
            return Image.open(out_p)
        except Exception as e:
            print(f"⚠️ 打开 skill 输出图失败: {e}")
            return None

    img = data.get("image")
    if isinstance(img, Image.Image):
        return img

    return None


def extract_skill_path(result: dict) -> Optional[str]:
    """只取路径，不加载图。"""
    if not result or result.get("status") != "success":
        return None
    data = result.get("result") or {}
    return data.get("output_path") or data.get("image_path")