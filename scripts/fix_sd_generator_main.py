# scripts/fix_sd_generator_main.py
"""修复 sd_generator/main.py 中的 KeyError: 'type' 问题"""
import re
from pathlib import Path

MAIN_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\sd_generator\main.py")

if not MAIN_FILE.exists():
    print("❌ 找不到 main.py")
    exit(1)

content = MAIN_FILE.read_text(encoding="utf-8")

# 1. 修复 models[0]['type'] 的访问
# 将 models[0]['type'].upper() 替换为 models[0].get('type', 'SD1.5').upper()
content = re.sub(
    r"models\[0\]\['type'\]\.upper\(\)",
    "models[0].get('type', 'SD1.5').upper()",
    content
)

# 2. 为了更安全，把后面可能出现的类似循环打印也修一下（如果有的话）
# 例如：for m in models: print(m['type']) -> print(m.get('type', ''))
content = re.sub(
    r"m\['type'\]",
    "m.get('type', 'Unknown')",
    content
)

MAIN_FILE.write_text(content, encoding="utf-8")
print("✅ 已修复 main.py 中的 KeyError: 'type' 问题")
print("\n👉 请重新运行: python apps/sd_generator/test_cli_core.py")
print("   或者直接运行: python apps/sd_generator/main.py")