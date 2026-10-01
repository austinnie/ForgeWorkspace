# scripts/fix_sd_gui_utils.py
"""补迁 sd-gui 缺失的 utils 目录"""
import shutil
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO")
WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# 优先从 sd-gui 复制，如果没有则从 sd_generator 复制
SOURCE_UTILS = OLD_ROOT / "sd-gui" / "utils"
if not SOURCE_UTILS.exists():
    SOURCE_UTILS = OLD_ROOT / "sd_generator" / "utils"

TARGET_UTILS = WORKSPACE / "apps" / "sd_gui" / "utils"

if SOURCE_UTILS.exists():
    print(f"📦 正在复制 utils 目录: {SOURCE_UTILS.relative_to(OLD_ROOT)} -> apps/sd_gui/utils")
    if TARGET_UTILS.exists():
        shutil.rmtree(TARGET_UTILS)
    shutil.copytree(SOURCE_UTILS, TARGET_UTILS, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("✅ utils 目录补迁成功！")
else:
    print("❌ 未找到源 utils 目录，请检查旧项目路径。")

print("\n👉 请重新运行: python apps/sd_gui/main.py")