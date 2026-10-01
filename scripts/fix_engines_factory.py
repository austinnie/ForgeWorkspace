# scripts/fix_engines_factory.py
"""修复 ForgeCore 引擎工厂函数，恢复正确的参数解包"""
from pathlib import Path

engines_init = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\engines\__init__.py")

new_content = '''# forgecore/engines/__init__.py
"""API 图像生成引擎 - 统一网关 (工厂模式)"""
import os

# 1. 导入所有引擎类 (基于 LayerForge 搬过来的代码)
from .base import BaseEngine
from .tongyi import TongyiEngine
from .yige import YigeEngine
from .hunyuan import HunyuanEngine
from .huggingface import HuggingFaceEngine
from .pollinations import PollinationsEngine
from .agnes import AgnesEngine
from .freeapi import FreeAPIEngine

# 尝试导入 ArtForge 新增的引擎 (如果后续搬过来会自动生效)
try: from .siliconflow import SiliconFlowEngine
except ImportError: SiliconFlowEngine = None

try: from .replicate import ReplicateEngine
except ImportError: ReplicateEngine = None

try: from .stability import StabilityEngine
except ImportError: StabilityEngine = None


def create_engine(provider: str, config: dict = None) -> BaseEngine:
    """
    统一引擎创建接口（兼容 LayerForge / ArtForge / PromptForge 调用方式）
    
    用法:
        engine = create_engine("pollinations")          # 免费，无需 Key
        engine = create_engine("agnes")                 # 自动从 .env 读取 Key
        engine = create_engine("tongyi", {"TONGYI_API_KEY": "xxx"})  # 手动传 Key
    """
    if config is None:
        config = {}
    
    provider = provider.lower().strip()
    
    # 🔥 自动从环境变量补充缺失的 Key (兼容 .env)
    env_keys = [
        "AGNES_API_KEY", "AGNES_BASE_URL", "AGNES_IMAGE_MODEL",
        "AGNES_VIDEO_MODEL", "AGNES_VISION_MODEL", "AGNES_TEXT_MODEL",
        "TONGYI_API_KEY", "TONGYI_MODEL",
        "YIGE_API_KEY", "YIGE_SECRET_KEY",
        "HUNYUAN_SECRET_ID", "HUNYUAN_SECRET_KEY",
        "HF_API_TOKEN", "HF_MODEL",
        "POLLINATIONS_API_KEY", "POLLINATIONS_MODEL",
        "FREEAPI_MODEL",
    ]
    for key in env_keys:
        if key not in config:
            val = os.getenv(key)
            if val:
                config[key] = val
    
    # 🔥 工厂模式：根据 provider 实例化对应的引擎 (严格匹配各引擎的 __init__ 签名)
    if provider == "tongyi":
        return TongyiEngine(
            api_key=config.get("TONGYI_API_KEY"),
            model=config.get("TONGYI_MODEL", "wanx-v1")
        )
    elif provider == "yige":
        return YigeEngine(
            api_key=config.get("YIGE_API_KEY"),
            secret_key=config.get("YIGE_SECRET_KEY")
        )
    elif provider == "hunyuan":
        return HunyuanEngine(
            secret_id=config.get("HUNYUAN_SECRET_ID"),
            secret_key=config.get("HUNYUAN_SECRET_KEY")
        )
    elif provider == "huggingface":
        return HuggingFaceEngine(
            api_token=config.get("HF_API_TOKEN"),
            model=config.get("HF_MODEL", "sdxl")
        )
    elif provider == "pollinations":
        # Pollinations 免费引擎，通常只需要 model 参数
        return PollinationsEngine(
            model=config.get("POLLINATIONS_MODEL")
        )
    elif provider == "agnes":
        return AgnesEngine(
            api_key=config.get("AGNES_API_KEY"),
            base_url=config.get("AGNES_BASE_URL"),
            image_model=config.get("AGNES_IMAGE_MODEL"),
            text_model=config.get("AGNES_TEXT_MODEL"),
            video_model=config.get("AGNES_VIDEO_MODEL"),
            vision_model=config.get("AGNES_VISION_MODEL"),
        )
    elif provider == "freeapi":
        return FreeAPIEngine(
            model=config.get("FREEAPI_MODEL", "grok-imagine-image-lite")
        )
    elif provider == "siliconflow" and SiliconFlowEngine:
        return SiliconFlowEngine(
            api_key=config.get("SILICONFLOW_API_KEY"),
            model=config.get("SILICONFLOW_MODEL")
        )
    elif provider == "replicate" and ReplicateEngine:
        return ReplicateEngine(
            api_token=config.get("REPLICATE_API_TOKEN"),
            model=config.get("REPLICATE_MODEL")
        )
    elif provider == "stability" and StabilityEngine:
        return StabilityEngine(
            api_key=config.get("STABILITY_API_KEY"),
            model=config.get("STABILITY_MODEL")
        )
    else:
        raise ValueError(f"❌ 不支持的 API 引擎: {provider}")

# 🔥 兼容 LayerForge 旧接口
create_api_engine = create_engine

__all__ = [
    "BaseEngine", "create_engine", "create_api_engine",
    "TongyiEngine", "YigeEngine", "HunyuanEngine", "HuggingFaceEngine",
    "PollinationsEngine", "AgnesEngine", "FreeAPIEngine"
]
'''

engines_init.write_text(new_content.strip(), encoding="utf-8")
print(f"✅ 已修复: {engines_init.relative_to(engines_init.parent.parent)}")
print("👉 请重新运行: python apps/artforge/main.py")