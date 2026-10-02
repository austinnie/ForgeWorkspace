# forgecore/pipeline/base_step.py
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
        

    def execute(self, context, progress_cb=None):
        """
        默认的 execute 实现 - 兼容旧代码
        如果子类没有重写此方法，将使用基于 Prompt 的 Mock 实现
        """
        if progress_cb:
            progress_cb(0.1, "准备提示词...")
        
        # 获取该风格的提示词
        prompts = self.get_prompts()
        if not prompts:
            # 如果没有预设提示词，使用默认值
            prompt_text = f"{self.name} style, masterpiece, best quality"
            negative_text = "worst quality, low quality"
        else:
            # 使用第一个场景的提示词
            prompt_text = prompts[0].get("prompt", f"{self.name} style")
            negative_text = prompts[0].get("negative", "worst quality, low quality")
        
        if progress_cb:
            progress_cb(0.5, "模拟风格转换...")
        
        # Mock 实现：在输入图片上添加文字标注（证明 Step 被执行）
        from PIL import Image, ImageDraw, ImageFont
        output_image = context.input_image.copy() if context.input_image else Image.new('RGB', (512, 512), color='white')
        draw = ImageDraw.Draw(output_image)
        
        # 在图片右下角添加风格名称
        text = f"[{self.name}]"
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
            
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置（右下角）
        x = output_image.width - text_width - 10
        y = output_image.height - text_height - 10
        
        # 绘制半透明背景
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill=(0, 0, 0, 128))
        # 绘制文字
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        if progress_cb:
            progress_cb(1.0, "风格转换完成")
        
        from .base import StepResult, StepStatus
        return StepResult(
            status=StepStatus.SUCCESS,
            output_image=output_image,
            metadata={
                "style": self.name,
                "prompt": prompt_text,
                "negative": negative_text,
                "mock": True
            }
        )

    def get_output_dir_name(self) -> str:
        return self.name or self.__class__.__name__
