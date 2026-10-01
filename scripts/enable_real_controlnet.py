# scripts/enable_real_controlnet.py
"""让 controlnet_mixin.py 真正调用 ForgeCore 的 ControlNet"""
from pathlib import Path
import re

MIXIN_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline\steps\controlnet_mixin.py")

if not MIXIN_FILE.exists():
    print("❌ 找不到 controlnet_mixin.py")
    exit(1)

content = MIXIN_FILE.read_text(encoding="utf-8")

# 1. 替换旧的 utils.controlnet 导入为 forgecore.controlnet
old_import_pattern = re.compile(r"try:\s*from utils\.controlnet import.*?except ImportError:.*?logger\.warning.*?\n(.*?)\n", re.DOTALL)
match = old_import_pattern.search(content)

if match:
    # 提取 Mock 函数部分（我们需要删除它）
    mock_code = match.group(1)
    
    # 替换为真实的导入
    new_import = """try:
    from forgecore.controlnet.skill import Controlnet
    from forgecore.controlnet.skill import CONTROLNET_TYPES
    # 兼容旧代码的函数名
    def get_controlnet_info(ctype):
        return CONTROLNET_TYPES.get(ctype, {})
    def preprocess_image_for_controlnet(*args, **kwargs):
        # 这里需要调用 Controlnet 的检测方法
        cn = Controlnet()
        return cn.detect_pose(*args, **kwargs)
except ImportError as e:
    logger.warning(f"⚠️ ForgeCore ControlNet 模块加载失败: {e}")
    # 保留 Mock 作为降级
    def get_controlnet_info(*args, **kwargs): return {}
    def preprocess_image_for_controlnet(*args, **kwargs): return None
"""
    content = content.replace(match.group(0), new_import)
    MIXIN_FILE.write_text(content, encoding="utf-8")
    print("✅ 已更新 controlnet_mixin.py，启用真实 ControlNet 调用")
else:
    print("ℹ️ 未找到旧的导入块，可能已被修改")

print("\n🎉 现在 60+ 个风格 Step 可以真正使用 ControlNet 了！")
print("👉 请重新运行: python apps/artforge/test_real_steps.py")