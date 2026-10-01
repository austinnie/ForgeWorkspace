# scripts/migrate_controlnet_module.py
"""迁移 sd_generator 的完整 ControlNet 模块到 ForgeCore"""
import shutil
import re
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO")
NEW_CONTROLNET_DIR = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\controlnet")

# 1. 定位源目录
SOURCE_DIR = OLD_ROOT / "sd_generator" / "core" / "controlnet"
if not SOURCE_DIR.exists():
    print(f"❌ 未找到源目录: {SOURCE_DIR}")
    exit(1)

print(f" 找到源目录: {SOURCE_DIR}")
print(f"📦 目标目录: {NEW_CONTROLNET_DIR}\n")

# 2. 复制整个 controlnet 文件夹
if NEW_CONTROLNET_DIR.exists():
    shutil.rmtree(NEW_CONTROLNET_DIR)
shutil.copytree(SOURCE_DIR, NEW_CONTROLNET_DIR)

# 3. 修复导入路径
print("🔧 正在修复导入路径...")
for py_file in NEW_CONTROLNET_DIR.rglob("*.py"):
    content = py_file.read_text(encoding="utf-8")
    original = content
    
    # 修复 utils.logger
    content = re.sub(r"from\s+utils\.logger\s+import\s+get_logger.*?\n", "import logging\nlogger = logging.getLogger('forgecore.controlnet')\n", content)
    
    # 修复 config.app
    content = re.sub(r"from\s+config\.app\s+import\s+.*?\n", "# [ForgeCore] 移除旧项目 config.app 依赖\n", content)
    
    # 修复相对导入 (from .skill import ...) 保持不变，但确保模块名正确
    # 修复 sys.path 插入 (旧代码可能有 sys.path.insert)
    content = re.sub(r"sys\.path\.insert\(0,.*?\n", "", content)
    
    if content != original:
        py_file.write_text(content, encoding="utf-8")

print("✅ 导入路径修复完成")

# 4. 更新 forgecore/__init__.py 导出
forgecore_init = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\__init__.py")
init_content = forgecore_init.read_text(encoding="utf-8")
if "controlnet" not in init_content:
    init_content += "\n# ControlNet 模块\ntry:\n    from .controlnet import Controlnet\nexcept ImportError:\n    pass\n"
    forgecore_init.write_text(init_content, encoding="utf-8")
    print("✅ 已更新 forgecore/__init__.py")

print("\n" + "="*60)
print("🎉 ControlNet 完整模块迁移完毕！")
print(" 现在 forgecore/controlnet/ 包含:")
print("   - skill.py (核心技能类)")
print("   - download_controlnet.py (模型下载)")
print("   - test_controlnet.py (测试脚本)")
print("="*60)