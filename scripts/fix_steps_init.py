# scripts/fix_steps_init.py
"""修复 steps 目录：删除旧依赖，实现 Step 自动发现与注册"""
from pathlib import Path

STEPS_DIR = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline\steps")

# 1. 删除旧的 controlnet_mixin.py (避免 utils.controlnet 报错)
cn_mixin = STEPS_DIR / "controlnet_mixin.py"
if cn_mixin.exists():
    cn_mixin.unlink()
    print("✅ 已删除 steps/controlnet_mixin.py (使用 base_step.py 中的空壳)")

# 2. 重写 steps/__init__.py (实现自动发现与注册)
init_content = '''# forgecore/pipeline/steps/__init__.py
"""自动发现、导入并注册所有风格转换 Step"""
import importlib
import pkgutil
import inspect
from pathlib import Path

from forgecore.pipeline.base_step import BaseStyleStep
from forgecore.pipeline.registry import PipelineRegistry

# 1. 自动导入当前目录下的所有模块
package_path = Path(__file__).parent
for (_, module_name, _) in pkgutil.iter_modules([str(package_path)]):
    if module_name != "__init__":
        try:
            importlib.import_module(f"{__package__}.{module_name}")
        except Exception as e:
            print(f"⚠️ 加载 Step 模块 {module_name} 失败: {e}")

# 2. 自动发现所有继承自 BaseStyleStep 的类，并注册到 PipelineRegistry
import sys
current_module = sys.modules[__name__]

registered_count = 0
for name, obj in inspect.getmembers(current_module):
    # 查找所有继承自 BaseStyleStep 的类 (排除 BaseStyleStep 本身)
    if inspect.isclass(obj) and issubclass(obj, BaseStyleStep) and obj is not BaseStyleStep:
        try:
            # 尝试实例化以获取 self.name (旧代码中通常在 __init__ 中定义)
            instance = obj()
            step_name = getattr(instance, "name", name.replace("Step", "").lower())
            PipelineRegistry.register_step(step_name, obj)
            registered_count += 1
        except Exception as e:
            # 如果实例化失败，使用类名推导 (例如 WatercolorStep -> watercolor)
            step_name = name.replace("Step", "").lower()
            PipelineRegistry.register_step(step_name, obj)
            registered_count += 1

print(f"🚀 自动发现并注册了 {registered_count} 个风格 Step！")

# 3. 导出所有 Step 类
__all__ = [name for name, obj in inspect.getmembers(current_module) 
           if inspect.isclass(obj) and issubclass(obj, BaseStyleStep) and obj is not BaseStyleStep]
'''

(STEPS_DIR / "__init__.py").write_text(init_content, encoding="utf-8")
print("✅ 已重写 steps/__init__.py (支持自动注册)")

print("\n🎉 修复完毕！")
print("👉 请重新运行: python apps/artforge/test_real_steps.py")