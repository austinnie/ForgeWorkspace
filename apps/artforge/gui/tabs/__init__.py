# apps/artforge/gui/tabs/__init__.py
"""ArtForge GUI - Tab 模块集合"""

from .generation_tab import build_generation_tab
from .img2img_tab import build_img2img_tab
from .pixel_magic_tab import build_pixel_magic_tab
from .skill_hub_tab import build_skill_hub_tab
from .chat_tab import build_chat_tab
from .config_tab import build_config_tab

__all__ = [
    "build_generation_tab",
    "build_img2img_tab",
    "build_pixel_magic_tab",
    "build_skill_hub_tab",
    "build_chat_tab",
    "build_config_tab",
]