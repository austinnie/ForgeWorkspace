# scripts/migrate_real_steps.py
"""一键搬迁 50+ 真实风格 Step 到 ForgeCore，并自动修复导入路径"""
import os
import shutil
import re
from pathlib import Path

# 📍 路径配置
OLD_ROOT = Path(r"E:\SD_OpenVINO")
NEW_STEPS_DIR = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline\steps")
NEW_STEPS_DIR.mkdir(parents=True, exist_ok=True)

# 尝试在旧项目中定位 steps 目录 (按优先级搜索)
CANDIDATE_PATHS = [
    OLD_ROOT / "sd_generator" / "core" / "pipeline" / "steps",
    OLD_ROOT / "sd-gui" / "core" / "pipeline" / "steps",
    OLD_ROOT / "tools" / "core" / "pipeline" / "steps",
    OLD_ROOT / "LayerForge" / "core" / "pipeline" / "steps",
]

SOURCE_STEPS_DIR = None
for p in CANDIDATE_PATHS:
    if p.exists() and any(p.glob("*.py")):
        SOURCE_STEPS_DIR = p
        break

if not SOURCE_STEPS_DIR:
    print("❌ 未找到旧项目的 steps 目录！")
    print("💡 请手动将旧项目中的 pipeline/steps 文件夹复制到:")
    print(f"   {NEW_STEPS_DIR}")
    exit(1)

print(f"🎯 找到源目录: {SOURCE_STEPS_DIR}")
print(f"📦 目标目录: {NEW_STEPS_DIR}\n")

# 1. 复制所有 .py 文件 (排除 __init__.py 和 __pycache__)
py_files = [f for f in SOURCE_STEPS_DIR.glob("*.py") if f.stem not in ("__init__",)]
print(f"📂 准备迁移 {len(py_files)} 个 Step 文件...")

for f in py_files:
    shutil.copy2(f, NEW_STEPS_DIR / f.name)

# 2. 批量修复导入路径 (将旧项目的 import 替换为 forgecore)
print("\n🔧 正在自动修复导入路径...")
# 匹配类似: from core.pipeline import PipelineStep, StepContext
# 或: from core.pipeline.base import ...
IMPORT_PATTERNS = [
    (re.compile(r"from\s+core\.pipeline(\.base)?\s+import"), "from forgecore.pipeline.base import"),
    (re.compile(r"from\s+\.\.base\s+import"), "from forgecore.pipeline.base import"), # 相对导入
    (re.compile(r"from\s+\.\.registry\s+import"), "from forgecore.pipeline.registry import"),
]

fixed_count = 0
for f in NEW_STEPS_DIR.glob("*.py"):
    content = f.read_text(encoding="utf-8")
    original = content
    
    for pattern, replacement in IMPORT_PATTERNS:
        content = pattern.sub(replacement, content)
        
    if content != original:
        f.write_text(content, encoding="utf-8")
        fixed_count += 1

print(f"✅ 已修复 {fixed_count} 个文件的导入路径")

# 3. 生成 steps/__init__.py (自动发现并导出所有 Step)
print("\n📝 生成 steps/__init__.py...")
init_content = '''# forgecore/pipeline/steps/__init__.py
"""自动发现并注册所有风格转换 Step"""
import importlib
import pkgutil
from pathlib import Path

# 1. 自动导入当前目录下的所有模块
package_path = Path(__file__).parent
for (_, module_name, _) in pkgutil.iter_modules([str(package_path)]):
    if module_name != "__init__":
        try:
            importlib.import_module(f"{__package__}.{module_name}")
        except Exception as e:
            print(f"⚠️ 加载 Step 模块 {module_name} 失败: {e}")

# 2. 导出所有在模块中定义的 Step 类 (以 Step 结尾的类)
__all__ = []
import sys
current_module = sys.modules[__name__]
for name in dir(current_module):
    if name.endswith("Step") and name not in ("BaseStep", "PipelineStep"):
        __all__.append(name)
'''
(NEW_STEPS_DIR / "__init__.py").write_text(init_content.strip(), encoding="utf-8")

print("\n" + "="*50)
print("🎉 50+ 真实风格 Step 搬迁完毕！")
print("💡 下一步: 运行 python apps/artforge/test_real_steps.py 验证真实效果")
print("="*50)