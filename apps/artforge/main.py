#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge (Gradio 版) - 支持本地模型与 API 双引擎启动器"""
import sys
import os
from pathlib import Path

# ============================================================
# 1. 路径注入 (保持原有逻辑，确保 ArtForge 内部模块兼容)
# ============================================================
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

# ============================================================
# 2. 加载环境变量
# ============================================================
ENV_PATH = APP_ROOT.parent.parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass

# ============================================================
# 3. 初始化 ForgeCore 全局配置与引擎状态
# ============================================================
print("=" * 60)
print(" 正在启动: ArtForge (Gradio 版)")
print("=" * 60)

try:
    # 导入 ForgeCore 核心配置 (如果已创建)
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    
    # 确保必要目录存在
    Paths.ensure_dirs()
    
    # 检查当前引擎模式 (读取 .env 中的 USE_LOCAL_MODEL)
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    base_models_dir = os.getenv("BASE_MODELS_DIR", r"E:\SD_OpenVINO\models")
    
    print(f"📂 模型基目录 (绝对路径): {base_models_dir}")
    print(f"📂 输出目录: {Paths.OUTPUT_DIR.resolve()}")
    
    if use_local:
        print("⚙️  当前模式: 🟢 本地模型模式 (Local Engine)")
        # 扫描本地可用模型，验证路径配置是否生效
        sd15_models = ModelRegistry.scan_checkpoints("sd15")
        sdxl_models = ModelRegistry.scan_checkpoints("sdxl")
        
        print(f"  ├─ 发现 SD1.5 模型: {len(sd15_models)} 个")
        if sd15_models:
            print(f"  │  ─ 默认: {sd15_models[0]['name']} ({sd15_models[0]['size_mb']}MB)")
            
        print(f"  └─ 发现 SDXL 模型: {len(sdxl_models)} 个")
        if sdxl_models:
            print(f"     └─ 默认: {sdxl_models[0]['name']} ({sdxl_models[0]['size_mb']}MB)")
    else:
        print("⚙️  当前模式: 🔵 云端 API 模式 (API Engine)")
        print("  └─ 提示: 在 .env 中设置 USE_LOCAL_MODEL=true 可切换为本地离线模式")
        
except ImportError as e:
    print(f"⚠️  ForgeCore 配置模块导入失败: {e}")
    print("💡 请确保 forgecore/forgecore/config/ 目录及文件已正确创建。")
except Exception as e:
    print(f"⚠️  初始化配置时出错: {e}")

print("-" * 60)

# ============================================================
# 4. 启动 GUI
# ============================================================
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
    input("按回车键退出...")