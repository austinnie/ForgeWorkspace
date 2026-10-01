# scripts/fix_skill_indentation_v2.py
"""精准修复 skill.py 中的缩进错误和 SD_MODEL_PATH 依赖"""
from pathlib import Path
import re

SKILL_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\controlnet\skill.py")

if not SKILL_FILE.exists():
    print("❌ 找不到 skill.py")
    exit(1)

content = SKILL_FILE.read_text(encoding="utf-8")

# ============================================================
# 步骤 1: 在文件顶部安全注入 SD_MODEL_PATH 定义，防止 NameError
# ============================================================
# 如果文件中没有全局定义 SD_MODEL_PATH，则在开头添加
if "SD_MODEL_PATH = os.environ" not in content and "SD_MODEL_PATH =" not in content.split("class ")[0]:
    header = "import os\n\n# [ForgeCore 兼容] 全局默认模型路径，可通过环境变量覆盖\nSD_MODEL_PATH = os.environ.get('SD_MODEL_PATH', None)\n\n"
    # 找到第一个 import 或 class 的位置插入
    match = re.search(r"^(import |from |class )", content, re.MULTILINE)
    if match:
        insert_pos = match.start()
        content = content[:insert_pos] + header + content[insert_pos:]
    else:
        content = header + content
    print("✅ 已在顶部注入 SD_MODEL_PATH 全局定义")

# ============================================================
# 步骤 2: 精准定位并修复缩进错误的代码块
# ============================================================
lines = content.split('\n')
fixed = False

for i, line in enumerate(lines):
    # 定位到报错的那一行：self.default_model_path = SD_MODEL_PATH
    if 'self.default_model_path = SD_MODEL_PATH' in line and i > 200:
        print(f"🔍 找到出错行: 第 {i+1} 行")
        
        # 向上寻找最近的 "if self.default_model_path is None:"
        start_idx = i
        while start_idx > 0 and "if self.default_model_path is None" not in lines[start_idx]:
            start_idx -= 1
            
        if start_idx >= 0:
            print(f"🔍 找到对应的 if 语句: 第 {start_idx+1} 行")
            
            # 获取 if 语句的基准缩进
            base_indent = lines[start_idx][:len(lines[start_idx]) - len(lines[start_idx].lstrip())]
            
            # 构建全新的、缩进绝对正确的代码块
            new_block = [
                f"{base_indent}if self.default_model_path is None:",
                f"{base_indent}    # [ForgeCore 修复] 从环境变量获取，替代旧 config.app",
                f"{base_indent}    self.default_model_path = os.environ.get('SD_MODEL_PATH', None)",
                f"{base_indent}    if self.default_model_path:",
                f"{base_indent}        print(f' 📦 从环境变量读取默认模型: {{self.default_model_path}}')",
            ]
            
            # 替换从 start_idx 到 i 的所有行（包括中间损坏的 try/except）
            lines[start_idx:i+1] = new_block
            fixed = True
            print("✅ 已重写该代码块，缩进已修复")
            break

if not fixed:
    print("⚠️ 未找到目标代码块，可能结构已变化。")
else:
    # 写回文件
    SKILL_FILE.write_text('\n'.join(lines), encoding="utf-8")
    print("\n skill.py 修复完毕！")
    print("👉 请重新运行: python apps/artforge/test_real_steps.py")