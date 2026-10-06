#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge (Gradio 版) - 终极修复版启动器"""
import sys
import os
from pathlib import Path
import gradio as gr
# 🔥 核心修复：路径注入逻辑
APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent.parent  # 指向 E:\SD_OpenVINO\ForgeWorkspace

# 1. 将项目根目录加入 sys.path (确保能 import forgecore.xxx)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 2. 将 ArtForge 自身目录加入 sys.path (确保能 import gui.xxx, config.xxx)
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 3. 加载环境变量
ENV_PATH = PROJECT_ROOT / ".env"
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
    # 初始化 ForgeCore 全局配置
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    
    Paths.ensure_dirs()
    
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    base_models_dir = os.getenv("BASE_MODELS_DIR", r"E:\SD_OpenVINO\models")
    
    print(f"📂 模型基目录 (绝对路径): {base_models_dir}")
    print(f"📂 输出目录: {Paths.OUTPUT_DIR.resolve()}")
    
    if use_local:
        print("⚙️  当前模式: 🟢 本地模型模式 (Local Engine)")
        sd15_models = ModelRegistry.scan_checkpoints("sd15")
        sdxl_models = ModelRegistry.scan_checkpoints("sdxl")
        
        print(f"  ├─ 发现 SD1.5 模型: {len(sd15_models)} 个")
        if sd15_models: print(f"  │  ─ 默认: {sd15_models[0]['name']} ({sd15_models[0]['size_mb']}MB)")
            
        print(f"  └─ 发现 SDXL 模型: {len(sdxl_models)} 个")
        if sdxl_models: print(f"     └─ 默认: {sdxl_models[0]['name']} ({sdxl_models[0]['size_mb']}MB)")
    else:
        print("⚙️  当前模式: 🔵 云端 API 模式 (API Engine)")
        
except Exception as e:
    print(f"⚠️  初始化配置时出错: {e}")

print("-" * 60)

# 启动 GUI
try:
    import gui.app as artforge_gui
    
    if hasattr(artforge_gui, 'build_ui'):
        print("🎯 找到 build_ui() 函数，正在构建并启动界面...")
        demo = artforge_gui.build_ui()
        demo.launch(inbrowser=True, share=False, theme=gr.themes.Soft())
    else:
        print("❌ 未找到 build_ui() 函数。")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")