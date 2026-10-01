# scripts/fix_base_step.py
"""修复 BaseStyleStep 兼容层，让 60+ 个旧 Step 能够成功导入"""
from pathlib import Path

PIPELINE_DIR = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline")

# ============================================================
# 1. 创建 base_step.py (兼容旧版 sd-gui 的 BaseStyleStep)
# ============================================================
base_step_code = '''# forgecore/pipeline/base_step.py
"""兼容旧版 sd-gui 的 BaseStyleStep 和 ControlNetMixin"""
from .base import BaseStep, StepContext, StepResult, StepStatus
from typing import List, Dict, Any

class ControlNetMixin:
    """ControlNet 兼容空壳，避免旧代码 import 报错"""
    def apply_controlnet(self, *args, **kwargs):
        pass

class PipelineStep(BaseStep):
    """兼容旧版 PipelineStep 命名"""
    pass

class BaseStyleStep(PipelineStep, ControlNetMixin):
    """
    兼容旧版 sd-gui 的 BaseStyleStep
    旧代码中大量 Step 继承此类，并调用 get_prompts(), get_default_config() 等方法
    """
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description
        self._config = {}

    def get_default_config(self) -> dict:
        return self._config

    def get_config_schema(self) -> dict:
        return {}

    def get_prompts(self) -> List[Dict[str, str]]:
        """返回该风格的多场景提示词列表，子类可重写"""
        return []

    def set_config(self, config: dict):
        self._config.update(config)
        
    def get_output_dir_name(self) -> str:
        return self.name or self.__class__.__name__
'''

(PIPELINE_DIR / "base_step.py").write_text(base_step_code, encoding="utf-8")
print("✅ 已生成 forgecore/pipeline/base_step.py (兼容旧版 BaseStyleStep)")

# ============================================================
# 2. 更新 __init__.py 导出兼容类
# ============================================================
init_content = '''# forgecore/pipeline/__init__.py
from .base import BaseStep, StepContext, StepResult, StepStatus
from .runner import PipelineRunner
from .registry import PipelineRegistry, register_step
from .base_step import BaseStyleStep, PipelineStep, ControlNetMixin

__all__ = [
    "BaseStep", "StepContext", "StepResult", "StepStatus", 
    "PipelineRunner", "PipelineRegistry", "register_step",
    "BaseStyleStep", "PipelineStep", "ControlNetMixin"
]
'''
(PIPELINE_DIR / "__init__.py").write_text(init_content, encoding="utf-8")
print("✅ 已更新 forgecore/pipeline/__init__.py")

print("\n🎉 兼容层修复完毕！")
print("👉 请重新运行: python apps/artforge/test_real_steps.py")