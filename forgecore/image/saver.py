# forgecore/image/saver.py
"""通用图片保存工具"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image


def save_image(
    image: Image.Image,
    prefix: str = "output",
    output_dir: Optional[Path] = None,
    fmt: str = "png",
) -> str:
    """
    保存 PIL 图片，返回保存路径（失败返回空字符串）。

    Args:
        image: PIL Image
        prefix: 文件名前缀
        output_dir: 输出目录；None 时用 Paths.OUTPUT_DIR，失败回退 output/
        fmt: 扩展名（png / jpg / webp）
    """
    if image is None:
        return ""
    try:
        if output_dir is None:
            try:
                from forgecore.config.paths import Paths
                output_dir = Paths.OUTPUT_DIR
            except Exception:
                output_dir = Path("output")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = output_dir / f"{prefix}_{ts}.{fmt}"

        if fmt.lower() in ("jpg", "jpeg") and image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        image.save(path)
        return str(path)
    except Exception as e:
        print(f"⚠️ 保存图片失败: {e}")
        return ""