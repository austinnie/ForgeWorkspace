# scripts/fix_init_verbose.py
"""强制暴露错误：重写 steps/__init__.py，移除静默捕获，强制打印所有导入错误"""
from pathlib import Path

INIT_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline\steps\__init__.py")

content = '''# forgecore/pipeline/steps/__init__.py
"""安全自动发现并注册所有风格 Step (强制打印错误，不再静默)"""
import sys
import os
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
    import traceback; traceback.print_exc()
    sys.exit(1)

package_path = Path(__file__).parent
print(f"📁 扫描目录: {package_path}")

# 1. 强制加载所有模块，打印错误
for (_, module_name, _) in pkgutil.iter_modules([str(package_path)]):
    if module_name.startswith("__"):
        continue
    print(f"🔄 尝试加载: {module_name}...")
    try:
        # 尝试多种导入方式，确保能找到
        try:
            importlib.import_module(f"forgecore.pipeline.steps.{module_name}")
        except ModuleNotFoundError:
            try:
                importlib.import_module(f"forgecore.forgecore.pipeline.steps.{module_name}")
            except ModuleNotFoundError:
                # 如果包名不对，使用文件路径直接加载
                import importlib.util
                file_path = package_path / f"{module_name}.py"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)
    except Exception as e:
        print(f"  ❌ {module_name} 加载失败: {e}")
        # 打印详细错误，帮助诊断
        import traceback
        traceback.print_exc()

# 2. 自动发现并注册
registered_count = 0
current_module = sys.modules[__name__]
for name, obj in inspect.getmembers(current_module):
    if inspect.isclass(obj) and issubclass(obj, BaseStyleStep) and obj is not BaseStyleStep:
        try:
            instance = obj()
            step_name = getattr(instance, "name", name.replace("Step", "").lower())
            PipelineRegistry.register_step(step_name, obj)
            registered_count += 1
            print(f"  ✅ 注册: {step_name}")
        except Exception as e:
            print(f"  ⚠️ 注册 {name} 失败: {e}")

print(f"\\n🚀 成功注册了 {registered_count} 个风格 Step！")
__all__ = [name for name, obj in inspect.getmembers(current_module) 
           if inspect.isclass(obj) and issubclass(obj, BaseStyleStep) and obj is not BaseStyleStep]
'''

INIT_FILE.write_text(content.strip(), encoding="utf-8")
print("✅ 已重写 steps/__init__.py (强制打印错误版)")
print("👉 请重新运行: python apps/artforge/test_real_steps.py")