"""兼容层：markflow.utils.controlnet_config"""
import os
from pathlib import Path
from typing import Optional

from forgecore.config.paths import Paths


def resolve_controlnet_path(controlnet_type: str) -> Optional[str]:
    """解析 ControlNet 模型路径"""
    controlnet_dir = Paths.CONTROLNET_DIR
    if not controlnet_dir.exists():
        return None
    
    # 常见命名
    candidates = [
        controlnet_dir / controlnet_type,
        controlnet_dir / f"control_v11p_sd15_{controlnet_type}",
        controlnet_dir / f"control_v11f1p_sd15_{controlnet_type}",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    
    # 模糊搜索
    for p in controlnet_dir.iterdir():
        if controlnet_type in p.name.lower():
            return str(p)
    return None