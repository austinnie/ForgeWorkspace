# scripts/fix_sd_gui_missing_dirs.py
"""补迁 sd-gui 缺失的核心目录 (config, core, generators, data)"""
import shutil
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO\sd-gui")
NEW_ROOT = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\sd_gui")

# 需要补迁的核心目录
DIRS_TO_COPY = [
    "config",      # 包含 app_config.py, config_manager.py 等
    "core",        # 包含 janus.py, grid_runner.py 等核心逻辑
    "generators",  # 包含 single_generator.py, couple_generator.py 等
    "data",        # 包含 configs, templates 等完整数据
]

print("🚀 开始补迁 sd-gui 缺失的核心目录...\n")

for d in DIRS_TO_COPY:
    src = OLD_ROOT / d
    dst = NEW_ROOT / d
    
    if src.exists():
        print(f"📦 复制目录: {d}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.log"))
    else:
        print(f"⚠️ 未找到源目录: {src}")

print("\n✅ 核心目录补迁完毕！")
print("👉 请重新运行: python apps/sd_gui/main.py")