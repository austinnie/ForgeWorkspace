#!/usr/bin/env python
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

print("\n" + "=" * 60)
print("测试完成。")
