# scripts/migrate_to_forgecore.py
import os
import shutil
from pathlib import Path

# 📍 路径配置
OLD_ROOT = Path(r"E:\SD_OpenVINO")
WORKSPACE_ROOT = Path(r"E:\SD_OpenVINO\ForgeWorkspace")
NEW_CORE = WORKSPACE_ROOT / "forgecore" / "forgecore"

def copy_dir(src, dst, ignore_patterns=None):
    if src.exists():
        # 🔧 修复点：使用 WORKSPACE_ROOT 作为基准，并增加容错
        try: src_rel = src.relative_to(OLD_ROOT)
        except ValueError: src_rel = src.name
        
        try: dst_rel = dst.relative_to(WORKSPACE_ROOT)
        except ValueError: dst_rel = dst.name
        
        print(f"📦 复制目录: {src_rel} -> {dst_rel}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_patterns) if ignore_patterns else None)
    else:
        print(f"⚠️ 未找到源目录: {src}")

def copy_file(src, dst):
    if src.exists():
        try: src_rel = src.relative_to(OLD_ROOT)
        except ValueError: src_rel = src.name
        
        try: dst_rel = dst.relative_to(WORKSPACE_ROOT)
        except ValueError: dst_rel = dst.name
        
        print(f"📄 复制文件: {src_rel} -> {dst_rel}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        print(f"⚠️ 未找到源文件: {src}")

print("🚀 开始将旧项目核心代码迁移至 ForgeCore...\n")

# 1. 迁移 API 引擎 (以 LayerForge 为主，它的最全)
copy_dir(
    OLD_ROOT / "LayerForge" / "core" / "api_engines", 
    NEW_CORE / "engines",
    ignore_patterns=["__pycache__", "*.pyc"]
)

# 2. 迁移 提示词构建器
copy_file(OLD_ROOT / "ArtForge" / "core" / "prompt_builder.py", NEW_CORE / "prompt" / "builder.py")
copy_file(OLD_ROOT / "LayerForge" / "core" / "composer.py", NEW_CORE / "prompt" / "composer.py")

# 3. 迁移 图像后处理 (EXIF注入等)
copy_file(OLD_ROOT / "sd_generator" / "utils" / "exif_injector.py", NEW_CORE / "image" / "exif_injector.py")

# 4. 迁移 开发者工具 (代码收集)
copy_file(OLD_ROOT / "LayerForge" / "gather_code.py", NEW_CORE / "devtools" / "code_gather.py")

# 5. 迁移 共享预设 (把 ArtForge 的妖怪/唐风预设搬过来)
copy_dir(
    OLD_ROOT / "ArtForge" / "presets", 
    WORKSPACE_ROOT / "shared_assets" / "presets",
    ignore_patterns=["__pycache__"]
)

print("\n✅ 核心代码搬家完成！")
print("💡 提示：请检查 forgecore/engines 目录下是否有 base.py 和多个引擎文件。")