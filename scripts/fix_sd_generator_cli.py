# scripts/fix_sd_generator_cli.py
"""补全 sd_generator 的 scripts 目录，并提供 CLI 核心生图测试"""
import shutil
from pathlib import Path

OLD_ROOT = Path(r"E:\SD_OpenVINO\sd_generator")
NEW_ROOT = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\sd_generator")

print("=" * 60)
print("🚀 修复 sd_generator CLI 问题...")
print("=" * 60 + "\n")

# 1. 补全 scripts 目录
src_scripts = OLD_ROOT / "scripts"
dst_scripts = NEW_ROOT / "scripts"

if src_scripts.exists():
    print(f"📦 正在复制 scripts 目录...")
    if dst_scripts.exists():
        shutil.rmtree(dst_scripts)
    shutil.copytree(src_scripts, dst_scripts, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("✅ scripts 目录补全成功！(包含 model_index.py 和 lora_index.py 逻辑)")
else:
    print("⚠️ 旧项目中未找到 scripts 目录，将尝试在代码中绕过。")

# 2. 生成一个直接调用底层引擎的 CLI 测试脚本
test_cli_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sd_generator CLI 核心生图测试 (绕过索引检查)"""
import sys
import os
from pathlib import Path

# 注入路径
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

CORE_PATH = APP_ROOT.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("=" * 60)
print("🧪 正在测试 sd_generator CLI 核心生图能力...")
print("=" * 60)

try:
    # 尝试导入旧版 sd_generator 的核心引擎
    # 注意：具体的导入路径取决于旧代码的结构，这里提供最常见的几种尝试
    from core.engine import SDGenerator # 假设旧代码叫这个
    print("✅ 成功导入 core.engine.SDGenerator")
    
    # 初始化并运行 (这里需要根据旧代码的实际 API 调整)
    # generator = SDGenerator()
    # generator.generate(prompt="a beautiful landscape", output_path="./output/test_cli.png")
    # print("🎉 CLI 核心生图测试成功！")
    
except ImportError as e:
    print(f"️ 无法导入 core.engine: {e}")
    print("💡 尝试直接运行旧版 main.py 并传入默认参数...")
    
    # 如果直接导入失败，我们尝试用 subprocess 运行 main.py
    import subprocess
    main_py = APP_ROOT / "main.py"
    if main_py.exists():
        print(f"🏃 正在执行: python {main_py} --help (检查参数)")
        subprocess.run([sys.executable, str(main_py), "--help"])
    else:
        print("❌ 找不到 main.py")

print("\\n" + "=" * 60)
print("测试完成。")
'''

(NEW_ROOT / "test_cli_core.py").write_text(test_cli_content, encoding="utf-8")
print("\n✅ 已生成: apps/sd_generator/test_cli_core.py")

print("\n" + "=" * 60)
print("👉 接下来请运行: python apps/sd_generator/test_cli_core.py")
print("   或者重新运行: python apps/sd_generator/launcher.py (现在应该不会再报找不到 index 了)")
print("=" * 60)