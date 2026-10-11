# forgecore/engines/helpers.py
"""引擎层的通用便捷函数"""

from typing import Optional

from PIL import Image


def agnes_img2img(
    prompt: str,
    image: Image.Image,
    strength: float = 0.6,
    width: int = 768,
    height: int = 1024,
    config: Optional[dict] = None,
) -> Optional[Image.Image]:
    """
    调 Agnes API 图生图。
    兼容 engine.image_to_image 的两种签名（image= / images=[]）。
    返回 PIL Image 或 None。
    """
    from forgecore.engines import create_engine

    engine = create_engine("agnes", config)
    try:
        return engine.image_to_image(
            prompt=prompt,
            image=image,
            strength=strength,
            width=width,
            height=height,
        )
    except TypeError:
        return engine.image_to_image(
            prompt=prompt,
            images=[image],
            strength=strength,
        )