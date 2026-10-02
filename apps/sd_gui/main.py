#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SD GUI (ForgeCore Thin Shell) - 极简启动器"""
import sys
import os
import warnings
from pathlib import Path

# 1. 彻底屏蔽第三方库的烦人警告
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# 2. 定位当前 App 和 ForgeWorkspace 根目录
APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent.parent  # 指向 E:\SD_OpenVINO\ForgeWorkspace

# 3. 注入 ForgeCore 路径 (必须在 load_dotenv 之前或同时，取决于 dotenv 实现，但通常先加路径更安全)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 4. 【关键步骤】在任何 forgecore 导入之前，强制加载 .env
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        # override=True 确保 .env 中的值能覆盖系统环境变量
        load_dotenv(ENV_PATH, override=True)
        print(f"✅ 已加载配置文件: {ENV_PATH}")
    except ImportError:
        print("⚠️ python-dotenv 未安装，将依赖系统环境变量")
else:
    print(f"⚠️ 未找到 .env 文件: {ENV_PATH}")

# 5. 启动 GUI
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 正在启动: SD GUI (ForgeCore Thin Shell)")
    print(f"📂 ForgeCore 根目录: {PROJECT_ROOT}")
    
    # 调试：打印一下关键 Key 是否加载成功
    print(f"🔑 AGNES_API_KEY 状态: {'已配置' if os.getenv('AGNES_API_KEY') else '❌ 缺失'}")
    print("=" * 60)
    
    try:
        from gui.app import SDGuiApp
        app = SDGuiApp()
        app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")