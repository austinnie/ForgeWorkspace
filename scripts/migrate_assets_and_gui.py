# scripts/migrate_assets_and_gui.py
"""终极迁移：将旧项目的提示词、预设、模板、GUI 代码全部搬入 ForgeWorkspace"""
import shutil
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO")
WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

def copy_dir(src, dst, ignore_patterns=None):
    if src.exists():
        print(f"📦 复制目录: {src.relative_to(OLD_ROOT)} -> {dst.relative_to(WORKSPACE)}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_patterns) if ignore_patterns else None)
    else:
        print(f"⚠️ 未找到: {src}")

def copy_file(src, dst):
    if src.exists():
        print(f"📄 复制文件: {src.relative_to(OLD_ROOT)} -> {dst.relative_to(WORKSPACE)}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

print("=" * 60)
print("🚀 开始终极资产与 GUI 迁移...")
print("=" * 60 + "\n")

# ============================================================
# 1. 迁移 sd_gui 的核心资产 (最庞大)
# ============================================================
print("【1/4】迁移 sd_gui 资产...")
# GUI 代码
copy_dir(OLD_ROOT / "sd-gui" / "gui", WORKSPACE / "apps" / "sd_gui" / "gui", 
         ignore_patterns=["__pycache__", "*.pyc"])
# 提示词与模板
copy_dir(OLD_ROOT / "sd-gui" / "tools" / "prompts", WORKSPACE / "shared_assets" / "prompts" / "sd_gui",
         ignore_patterns=["__pycache__"])
copy_dir(OLD_ROOT / "sd-gui" / "tools" / "prompts_new", WORKSPACE / "shared_assets" / "prompts" / "sd_gui_new",
         ignore_patterns=["__pycache__"])
copy_dir(OLD_ROOT / "sd-gui" / "data" / "templates", WORKSPACE / "shared_assets" / "templates" / "sd_gui",
         ignore_patterns=["__pycache__"])
copy_dir(OLD_ROOT / "sd-gui" / "data" / "configs", WORKSPACE / "shared_assets" / "configs" / "sd_gui",
         ignore_patterns=["__pycache__"])

# ============================================================
# 2. 迁移 sd_generator 的提示词库
# ============================================================
print("\n【2/4】迁移 sd_generator 资产...")
copy_dir(OLD_ROOT / "sd_generator" / "prompts", WORKSPACE / "shared_assets" / "prompts" / "sd_generator",
         ignore_patterns=["__pycache__"])

# ============================================================
# 3. 迁移 LayerForge 的 6 层架构与预设
# ============================================================
print("\n【3/4】迁移 LayerForge 资产...")
# GUI
copy_dir(OLD_ROOT / "LayerForge" / "gui", WORKSPACE / "apps" / "layerforge" / "gui",
         ignore_patterns=["__pycache__"])
# 核心资产
copy_dir(OLD_ROOT / "LayerForge" / "layers", WORKSPACE / "shared_assets" / "layers" / "layerforge",
         ignore_patterns=["__pycache__"])
copy_dir(OLD_ROOT / "LayerForge" / "presets", WORKSPACE / "shared_assets" / "presets" / "layerforge",
         ignore_patterns=["__pycache__"])

# ============================================================
# 4. 迁移 ArtForge 和 PromptForge 的 GUI 与技能
# ============================================================
print("\n【4/4】迁移 ArtForge & PromptForge 资产...")
# ArtForge GUI
if (OLD_ROOT / "ArtForge" / "gui").exists():
    copy_dir(OLD_ROOT / "ArtForge" / "gui", WORKSPACE / "apps" / "artforge" / "gui",
             ignore_patterns=["__pycache__"])
# PromptForge Skills (这是 PromptForge 的核心)
copy_dir(OLD_ROOT / "PromptForge" / "skills", WORKSPACE / "apps" / "promptforge" / "skills",
         ignore_patterns=["__pycache__", "output"])
if (OLD_ROOT / "PromptForge" / "gui").exists():
    copy_dir(OLD_ROOT / "PromptForge" / "gui", WORKSPACE / "apps" / "promptforge" / "gui",
             ignore_patterns=["__pycache__"])

print("\n" + "=" * 60)
print("🎉 终极资产与 GUI 迁移完毕！")
print("💡 提示：GUI 代码中的导入路径 (如 from gui.xxx import) 需要后续修复。")
print("=" * 60)