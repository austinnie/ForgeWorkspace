#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LayerForge (Gradio 版) - Monorepo 启动器"""
import sys
import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

for extra in ["core", "config"]:
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
print("🚀 正在启动: LayerForge (Gradio 版)")
print("=" * 60)

try:
    import gui.gradio_app as gradio_app
    
    # 尝试多种方式启动，确保总能找到入口
    if hasattr(gradio_app, 'main'):
        print("🚀 调用 gradio_app.main()...")
        gradio_app.main()
    elif hasattr(gradio_app, 'demo') and hasattr(getattr(gradio_app, 'demo'), 'launch'):
        print(f"🚀 启动 Gradio 界面: demo.launch()...")
        getattr(gradio_app, 'demo').launch(inbrowser=True, share=False)
    else:
        print("⚠️ 未找到标准的启动入口，模块加载完毕。")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")

