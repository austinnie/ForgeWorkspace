#!/usr/bin/env python
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
