# forgecore/pipeline/steps/controlnet_mixin.py
"""ControlNet 混入类 - ForgeCore 终极干净版"""
import logging
logger = logging.getLogger('forgecore.pipeline.mixin')

# 优雅降级：尝试导入真实的 ControlNet，失败则提供 Mock
try:
    from forgecore.skills.controlnet.skill import Controlnet, CONTROLNET_TYPES
    def get_controlnet_info(ctype): return CONTROLNET_TYPES.get(ctype, {})
    def preprocess_image_for_controlnet(*args, **kwargs):
        cn = Controlnet()
        return cn.detect_pose(*args, **kwargs)
    CONTROLNET_AVAILABLE = True
except Exception as e:
    CONTROLNET_TYPES = {}
    def get_controlnet_info(*args, **kwargs): return {}
    def preprocess_image_for_controlnet(*args, **kwargs): return None
    CONTROLNET_AVAILABLE = False
    logger.warning(f"⚠️ ControlNet 模块未加载 (已降级为 Mock): {e}")

class ControlNetMixin:
    """为 StyleStep 提供 ControlNet 支持和场景数限制"""
    def _get_scene_limit(self) -> int:
        return getattr(self, '_scene_limit', 10)

    def _setup_controlnet(self, context, controlnet_type: str = "openpose"):
        if not CONTROLNET_AVAILABLE or not context.input_image:
            return None
        try:
            return preprocess_image_for_controlnet(context.input_image, controlnet_type=controlnet_type)
        except Exception as e:
            logger.error(f" ControlNet 预处理失败: {e}")
            return None

    def _check_memory(self, threshold_mb: int = 2048) -> bool:
        return True  # 简化内存检查
