#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SD GUI (Tkinter 桌面版) - Monorepo 启动器"""
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

# 3. 注入旧代码依赖的额外目录
for extra in ["tools", "core", "config", "utils"]:
    p = APP_ROOT / extra
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# 4. 加载全局 .env
ENV_PATH = APP_ROOT.parent.parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass

print("=" * 60)
print("🚀 正在启动: SD GUI (Tkinter 桌面版)")
print("=" * 60)

try:
    from gui.app import main
    main()
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")
