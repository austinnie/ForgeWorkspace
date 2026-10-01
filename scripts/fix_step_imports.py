# scripts/fix_step_imports.py
"""强制修复 60+ 个旧 Step 文件的导入路径，让它们真正继承 ForgeCore 的 BaseStyleStep"""
import re
from pathlib import Path

STEPS_DIR = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline\steps")
fixed_count = 0

# 定义需要替换的旧导入模式 -> 新导入
REPLACEMENTS = [
    # 模式 1: from ..base_step import BaseStyleStep
    (re.compile(r"from\s+\.\.\s*base_step\s+import\s+BaseStyleStep"), 
     "from forgecore.pipeline.base_step import BaseStyleStep"),
     
    # 模式 2: from core.pipeline.base_step import BaseStyleStep
    (re.compile(r"from\s+core\.pipeline\.base_step\s+import\s+BaseStyleStep"), 
     "from forgecore.pipeline.base_step import BaseStyleStep"),
     
    # 模式 3: from .base_step import BaseStyleStep
    (re.compile(r"from\s+\.base_step\s+import\s+BaseStyleStep"), 
     "from forgecore.pipeline.base_step import BaseStyleStep"),
     
    # 模式 4: from core.pipeline.steps.base_step import BaseStyleStep
    (re.compile(r"from\s+core\.pipeline\.steps\.base_step\s+import\s+BaseStyleStep"), 
     "from forgecore.pipeline.base_step import BaseStyleStep"),
     
    # 模式 5: 兼容旧版 PipelineStep
    (re.compile(r"from\s+core\.pipeline\.step\s+import\s+PipelineStep"), 
     "from forgecore.pipeline.base_step import PipelineStep"),
]

print("🔍 正在扫描并修复 steps 目录下的所有文件...\n")

for py_file in STEPS_DIR.glob("*.py"):
    if py_file.name == "__init__.py" or py_file.name == "base_step.py" or py_file.name == "controlnet_mixin.py":
        continue
        
    content = py_file.read_text(encoding="utf-8")
    original_content = content
    
    for pattern, replacement in REPLACEMENTS:
        content = pattern.sub(replacement, content)
        
    if content != original_content:
        py_file.write_text(content, encoding="utf-8")
        fixed_count += 1
        print(f"✅ 修复: {py_file.name}")

print(f"\n 共修复了 {fixed_count} 个 Step 文件的导入路径！")
print(" 请重新运行: python apps/artforge/test_real_steps.py")