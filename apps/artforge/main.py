#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge (Gradio 版) - 终极修复版启动器"""
import sys
import os
from pathlib import Path

# 1. 路径注入
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

for extra in ["core", "config", "api_engines", "skills"]:
    p = APP_ROOT / extra
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

ENV_PATH = APP_ROOT.parent.parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass

print("=" * 60)
print("🚀 正在启动: ArtForge (Gradio 版)")
print("=" * 60)

try:
    import gui.app as artforge_gui
    
    # 🔥 核心修复：显式调用 build_ui() 函数来获取 Gradio 实例
    if hasattr(artforge_gui, 'build_ui'):
        print("🎯 找到 build_ui() 函数，正在构建并启动界面...")
        demo = artforge_gui.build_ui()
        demo.launch(inbrowser=True, share=False)
    else:
        print("❌ 未找到 build_ui() 函数。")
        
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("\n按回车键退出...")
