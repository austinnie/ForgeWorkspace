# scripts/fix_skill_indentation.py
"""修复 skill.py 中因删除旧导入导致的缩进错误和变量未定义问题"""
from pathlib import Path
import re

SKILL_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\controlnet\skill.py")

if not SKILL_FILE.exists():
    print("❌ 找不到 skill.py")
    exit(1)

content = SKILL_FILE.read_text(encoding="utf-8")

# 定位并替换有问题的代码块
# 匹配从 "if self.default_model_path is None:" 到 "except Exception as e:" 之后的内容
old_block_pattern = re.compile(
    r"if self\.default_model_path is None:\s*try:.*?except Exception as e:\s*logger\.warning\(f\" ⚠️ 读取 SD_MODEL_PATH 失败: \{e\}\"\)",
    re.DOTALL
)

new_block = """if self.default_model_path is None:
        # 🔥 [ForgeCore 修复] 从环境变量或全局配置读取，替代旧项目的 config.app
        self.default_model_path = os.environ.get('SD_MODEL_PATH', None)
        if self.default_model_path:
            logger.info(f" 📦 从环境变量读取默认模型: {self.default_model_path}")
        else:
            logger.warning(" ⚠️ 未设置默认模型路径 (SD_MODEL_PATH)，请在 config 或 .env 中指定")"""

if old_block_pattern.search(content):
    content = old_block_pattern.sub(new_block, content)
    SKILL_FILE.write_text(content, encoding="utf-8")
    print("✅ 已修复 skill.py 中的缩进错误和 SD_MODEL_PATH 读取逻辑")
else:
    print("ℹ️ 未找到匹配的代码块，可能已被修复或结构不同。请手动检查 skill.py 第 266 行附近。")

print("\n👉 请重新运行: python apps/artforge/test_real_steps.py")