# scripts/fix_sd_gui_services.py
"""补迁 sd-gui 缺失的 services 目录"""
import shutil
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO\sd-gui")
NEW_ROOT = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\sd_gui")

SOURCE_SERVICES = OLD_ROOT / "services"
TARGET_SERVICES = NEW_ROOT / "services"

if SOURCE_SERVICES.exists():
    print(f"📦 正在复制 services 目录: {SOURCE_SERVICES.relative_to(OLD_ROOT)} -> apps/sd_gui/services")
    if TARGET_SERVICES.exists():
        shutil.rmtree(TARGET_SERVICES)
    shutil.copytree(SOURCE_SERVICES, TARGET_SERVICES, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("✅ services 目录补迁成功！")
else:
    print(f"❌ 未找到源 services 目录: {SOURCE_SERVICES}")
    print("💡 请检查旧项目 E:\\SD_OpenVINO\\sd-gui 下是否有 services 文件夹。")

print("\n👉 请重新运行: python apps/sd_gui/main.py")