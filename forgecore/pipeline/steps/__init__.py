# forgecore/pipeline/steps/__init__.py
"""自动发现并注册所有风格 Step (注入命名空间版)"""
import sys
import importlib
import pkgutil
import inspect
import logging
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).resolve().parents[4] 
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print("🚀 开始加载 ForgeCore Steps...")

try:
    from forgecore.pipeline.base_step import BaseStyleStep
    from forgecore.pipeline.registry import PipelineRegistry
    print("✅ 基础类导入成功")
except Exception as e:
    print(f"❌ 基础类导入失败: {e}")
    sys.exit(1)

# 导入 ControlNetMixin (如果存在)
try:
    from .controlnet_mixin import ControlNetMixin
    print("✅ ControlNetMixin 导入成功")
except Exception as e:
    print(f"⚠️ ControlNetMixin 导入失败: {e}")

package_path = Path(__file__).parent
current_module = sys.modules[__name__]
registered_count = 0
failed_modules = []

# 1. 遍历并加载所有子模块
for (_, module_name, _) in pkgutil.iter_modules([str(package_path)]):
    if module_name.startswith("__"):
        continue
    
    full_module_name = f"forgecore.pipeline.steps.{module_name}"
    try:
        # 加载模块
        mod = importlib.import_module(full_module_name)
        
        # 🔥 核心修复：将子模块的所有公开属性注入到当前 __init__.py 的命名空间
        # 这样 inspect.getmembers(current_module) 才能找到它们！
        for attr_name in dir(mod):
            if not attr_name.startswith("_"):
                setattr(current_module, attr_name, getattr(mod, attr_name))
                
    except Exception as e:
        failed_modules.append(module_name)
        # 打印详细错误，帮助诊断
        import traceback
        print(f"  ❌ 加载 {module_name} 失败: {e}")
        traceback.print_exc()

# 2. 自动发现并注册所有继承自 BaseStyleStep 的类
for name, obj in inspect.getmembers(current_module):
    if inspect.isclass(obj) and issubclass(obj, BaseStyleStep) and obj is not BaseStyleStep:
        try:
            instance = obj()
            step_name = getattr(instance, "name", name.replace("Step", "").lower())
            PipelineRegistry.register_step(step_name, obj)
            registered_count += 1
        except Exception as e:
            # 如果实例化失败，使用类名推导
            step_name = name.replace("Step", "").lower()
            PipelineRegistry.register_step(step_name, obj)
            registered_count += 1

print(f"\n🚀 成功注册了 {registered_count} 个风格 Step！")
if failed_modules:
    print(f"⚠️ 以下模块加载失败: {failed_modules}")

__all__ = [name for name, obj in inspect.getmembers(current_module) 
           if inspect.isclass(obj) and issubclass(obj, BaseStyleStep) and obj is not BaseStyleStep]