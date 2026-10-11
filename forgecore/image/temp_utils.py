# forgecore/image/temp_utils.py
"""PIL 图片与临时文件互转的工具"""

import os
import tempfile

from PIL import Image


def pil_to_temp_png(image: Image.Image) -> str:
    """把 PIL Image 写进临时 PNG 文件，返回路径。调用方负责删除。"""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(tmp.name)
    return tmp.name


def safe_remove(path: str) -> None:
    """静默删除文件，不抛异常。"""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass