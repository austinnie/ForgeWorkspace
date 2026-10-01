# scripts/fix_gui_launchers.py
"""为所有 App 生成标准的 GUI 启动器 (main.py)，自动注入路径"""
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# 定义每个 App 的启动配置
APPS = {
    "sd_gui": {
        "gui_entry": "gui.app",  # 旧代码的主入口模块 (如 gui/app.py 中的 main 函数)
        "title": "SD GUI (Tkinter 桌面版)",
        "extra_paths": ["tools", "core", "config", "utils"]  # 旧代码依赖的额外目录
    },
    "layerforge": {
        "gui_entry": "gui.gradio_app", # 或者 gui.tk_app
        "title": "LayerForge (Gradio 版)",
        "extra_paths": ["core", "config"]
    },
    "artforge": {
        "gui_entry": "run_gui_Gradio", # ArtForge 的 Gradio 启动脚本
        "title": "ArtForge (Gradio 版)",
        "extra_paths": ["core", "config", "api_engines", "skills"]
    },
    "promptforge": {
        "gui_entry": "main", # PromptForge 通常是命令行或 FastAPI
        "title": "PromptForge",
        "extra_paths": ["core", "config", "skills"]
    }
}

LAUNCHER_TEMPLATE = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""{title} - Monorepo 启动器 (自动注入路径)"""
import sys
import os
from pathlib import Path

#  1. 定位当前 App 的根目录
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 🔥 2. 注入 ForgeCore 路径
CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

# 🔥 3. 注入旧代码依赖的额外目录 (如 tools/, core/, config/)
{extra_paths_injection}

# 🔥 4. 加载全局 .env
ENV_PATH = APP_ROOT.parent.parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass

# 🔥 5. 启动 GUI
print("=" * 60)
print("🚀 正在启动: {title}")
print("=" * 60)

try:
    {launch_code}
except Exception as e:
    print(f"❌ 启动失败: {{e}}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")
'''

print("️ 正在生成 GUI 启动器...\n")

for app_name, config in APPS.items():
    app_dir = WORKSPACE / "apps" / app_name
    main_py = app_dir / "main.py"
    
    # 生成额外路径注入代码
    extra_paths_code = "\n".join([
        f'EXTRA_PATH = APP_ROOT / "{p}"\nif EXTRA_PATH.exists() and str(EXTRA_PATH) not in sys.path:\n    sys.path.insert(0, str(EXTRA_PATH))'
        for p in config["extra_paths"]
    ])
    
    # 生成启动代码
    if app_name == "sd_gui":
        launch_code = '''from gui.app import main
main()'''
    elif app_name == "layerforge":
        launch_code = '''from gui.gradio_app import main
main()'''
    elif app_name == "artforge":
        launch_code = '''import run_gui_Gradio'''
    else:
        launch_code = '''print("✅ PromptForge 环境就绪，请使用 CLI 或 FastAPI 启动。")'''

    content = LAUNCHER_TEMPLATE.format(
        title=config["title"],
        extra_paths_injection=extra_paths_code,
        launch_code=launch_code
    )
    
    main_py.write_text(content, encoding="utf-8")
    print(f"✅ 已生成: apps/{app_name}/main.py")

print("\n" + "=" * 60)
print(" 所有 GUI 启动器生成完毕！")
print("💡 提示：现在您可以直接运行 python apps/sd_gui/main.py 启动桌面版了！")
print("=" * 60)