"""
兼容层：markflow.utils.model_config
转发到 forgecore.config.registry / paths
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from forgecore.config.registry import ModelRegistry
from forgecore.config.paths import Paths


def get_model_config(model_name: str = None) -> Dict[str, Any]:
    """兼容 markflow 的 get_model_config"""
    sd15 = ModelRegistry.scan_checkpoints("sd15")
    sdxl = ModelRegistry.scan_checkpoints("sdxl")
    
    all_models = sd15 + sdxl
    if model_name:
        target = next((m for m in all_models if m["name"] == model_name), None)
        if target:
            return {
                "model_path": target["absolute_path"],
                "model_type": target.get("type", "sd15"),
                "model_name": target["name"],
                "device": "cpu",
                "loras": [],
                "default_steps": 25,
                "default_cfg": 7.5,
            }
    
    if all_models:
        first = all_models[0]
        return {
            "model_path": first["absolute_path"],
            "model_type": first.get("type", "sd15"),
            "model_name": first["name"],
            "device": "cpu",
            "loras": [],
            "default_steps": 25,
            "default_cfg": 7.5,
        }
    
    return {
        "model_path": None,
        "model_type": "sd15",
        "model_name": None,
        "device": "cpu",
        "loras": [],
    }


def resolve_model_path(model_name: str = None) -> Optional[str]:
    """解析模型路径"""
    cfg = get_model_config(model_name)
    return cfg.get("model_path")


def resolve_lora_paths() -> List[Dict[str, Any]]:
    """解析 LoRA 路径"""
    try:
        sd15 = ModelRegistry.scan_loras("sd15")
        sdxl = ModelRegistry.scan_loras("sdxl")
        return [
            {"path": l["absolute_path"], "weight": 0.8, "name": l["name"]}
            for l in (sd15 + sdxl)
        ]
    except Exception:
        return []


def get_models() -> List[str]:
    """列出所有模型名"""
    sd15 = ModelRegistry.scan_checkpoints("sd15")
    sdxl = ModelRegistry.scan_checkpoints("sdxl")
    return [m["name"] for m in sd15 + sdxl]


def get_loras() -> List[str]:
    """列出所有 LoRA 名"""
    try:
        sd15 = ModelRegistry.scan_loras("sd15")
        sdxl = ModelRegistry.scan_loras("sdxl")
        return [l["name"] for l in sd15 + sdxl]
    except Exception:
        return []


def update_user_config_item(key: str, value):
    """兼容函数（暂时空实现）"""
    pass


# 兼容 markflow 里定义的常量
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:1.5b"
MODEL_TYPE = "sd15"
PROJECT_ROOT = Paths.OUTPUT_DIR.parent