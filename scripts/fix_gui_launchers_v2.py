# scripts/fix_gui_launchers_v2.py
"""彻底修复所有 App 的 GUI 启动器 (main.py)，确保语法 100% 正确"""
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# ============================================================
# 1. sd_gui (Tkinter 桌面版)
# ============================================================
sd_gui_main = '''#!/usr/bin/env python
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
'''
(WORKSPACE / "apps" / "sd_gui" / "main.py").write_text(sd_gui_main, encoding="utf-8")
print("✅ 已修复: apps/sd_gui/main.py")

# ============================================================
# 2. layerforge (Gradio 版)
# ============================================================
layerforge_main = '''#!/usr/bin/env python
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
    from gui.gradio_app import main
    main()
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")
'''
(WORKSPACE / "apps" / "layerforge" / "main.py").write_text(layerforge_main, encoding="utf-8")
print("✅ 已修复: apps/layerforge/main.py")

# ============================================================
# 3. artforge (Gradio 版)
# ============================================================
artforge_main = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge (Gradio 版) - Monorepo 启动器"""
import sys
import os
from pathlib import Path

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
    import run_gui_Gradio
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按回车键退出...")
'''
(WORKSPACE / "apps" / "artforge" / "main.py").write_text(artforge_main, encoding="utf-8")
print("✅ 已修复: apps/artforge/main.py")

# ============================================================
# 4. promptforge
# ============================================================
promptforge_main = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PromptForge - Monorepo 启动器"""
import sys
import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

for extra in ["core", "config", "skills"]:
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
print("🚀 正在启动: PromptForge")
print("=" * 60)
print("✅ PromptForge 环境就绪，请使用 CLI 或 FastAPI 启动。")
'''
(WORKSPACE / "apps" / "promptforge" / "main.py").write_text(promptforge_main, encoding="utf-8")
print("✅ 已修复: apps/promptforge/main.py")

print("\n 所有 GUI 启动器已彻底修复！")
print("👉 请重新运行: python apps/sd_gui/main.py")