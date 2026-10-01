# scripts/migrate_sd_generator_core.py
"""完整迁移 sd_generator 核心代码到 ForgeWorkspace"""
import shutil
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO")
WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# 目标目录
TARGET_DIR = WORKSPACE / "apps" / "sd_generator"

print("=" * 60)
print("🚀 开始迁移 sd_generator 核心代码...")
print("=" * 60 + "\n")

# 需要迁移的核心目录
CORE_DIRS = [
    "core",          # 核心生成逻辑 (engine.py, pipeline.py 等)
    "utils",         # 工具类 (logger, controlnet 等)
    "api_engines",   # API 引擎 (如果存在)
    "config",        # 配置文件 (如果存在)
    "skills",        # 技能模块 (如果存在)
]

# 1. 迁移核心目录
for d in CORE_DIRS:
    src = OLD_ROOT / "sd_generator" / d
    dst = TARGET_DIR / d
    
    if src.exists():
        print(f" 复制目录: sd_generator/{d} -> apps/sd_generator/{d}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.log"))
    else:
        print(f"⚠️ 未找到: sd_generator/{d}")

# 2. 迁移根目录下的关键单文件 (如 main.py, run.py, engine.py)
ROOT_FILES = ["main.py", "run.py", "engine.py", "app.py", "requirements.txt"]
for f in ROOT_FILES:
    src = OLD_ROOT / "sd_generator" / f
    dst = TARGET_DIR / f
    if src.exists():
        print(f"📄 复制文件: sd_generator/{f} -> apps/sd_generator/{f}")
        shutil.copy2(src, dst)

# 3. 生成标准的启动器 main.py (如果旧代码没有统一的入口)
launcher_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SD Generator (CLI/脚本版) - Monorepo 启动器"""
import sys
import os
from pathlib import Path

# 1. 定位当前 App 的根目录
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 2. 注入 ForgeCore 路径
CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

# 3. 加载全局 .env
ENV_PATH = APP_ROOT.parent.parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass

print("=" * 60)
print(" 正在启动: SD Generator (CLI 版)")
print("=" * 60)

# 尝试启动旧代码的主入口
try:
    # 优先尝试运行旧的 main.py 或 engine.py
    if (APP_ROOT / "main.py").exists() and (APP_ROOT / "main.py").resolve() != Path(__file__).resolve():
        import main
    elif (APP_ROOT / "engine.py").exists():
        import engine
    else:
        print("✅ SD Generator 环境就绪。")
        print("💡 提示：您可以直接调用 apps/sd_generator/core/ 中的模块。")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
'''

# 保存为 launcher.py 以免覆盖旧代码的 main.py
(TARGET_DIR / "launcher.py").write_text(launcher_content, encoding="utf-8")
print("\n✅ 已生成: apps/sd_generator/launcher.py (标准启动器)")

print("\n" + "=" * 60)
print("🎉 sd_generator 核心代码迁移完毕！")
print("💡 现在您可以运行: python apps/sd_generator/launcher.py")
print("=" * 60)