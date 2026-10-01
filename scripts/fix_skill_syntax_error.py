# scripts/fix_skill_syntax_error.py
"""彻底修复 skill.py 中因残留 except 导致的 SyntaxError"""
from pathlib import Path

file_path = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\controlnet\skill.py")
if not file_path.exists():
    print("❌ 找不到 skill.py")
    exit(1)

lines = file_path.read_text(encoding="utf-8").split('\n')

start_line = -1
try_line = -1
except_line = -1
end_line = -1

# 1. 找到 if self.default_model_path is None:
for i, line in enumerate(lines):
    if "if self.default_model_path is None:" in line and not line.strip().startswith("#"):
        start_line = i
        break
        
if start_line == -1:
    print("❌ 未找到 if self.default_model_path is None:")
    exit(1)
    
if_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

# 2. 找到它下面的 try:
for i in range(start_line + 1, len(lines)):
    if lines[i].strip() == "try:":
        try_line = i
        break
        
if try_line == -1:
    print(" 未找到 try:，可能结构已变化")
    exit(1)
    
# 3. 找到对应的 except ImportError:
for i in range(try_line + 1, len(lines)):
    if "except ImportError:" in lines[i]:
        except_line = i
        break
        
if except_line == -1:
    print("❌ 未找到 except ImportError:")
    exit(1)
    
# 4. 找到 except 块结束的位置 (下一个缩进 <= except_indent 的非空行)
except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
for i in range(except_line + 1, len(lines)):
    if lines[i].strip(): # 非空行
        current_indent = len(lines[i]) - len(lines[i].lstrip())
        if current_indent <= except_indent:
            end_line = i
            break
if end_line == -1:
    end_line = len(lines) # 如果到文件末尾都没找到，就替换到末尾
    
# 5. 构建完美的替换代码块
indent = " " * if_indent
new_block = [
    f"{indent}if self.default_model_path is None:",
    f"{indent}    # [ForgeCore 修复] 从环境变量获取，替代旧 config.app",
    f"{indent}    self.default_model_path = os.environ.get('SD_MODEL_PATH', None)",
    f"{indent}    if self.default_model_path:",
    f"{indent}        print(f' 📦 从环境变量读取默认模型: {{self.default_model_path}}')",
]

# 6. 执行替换：保留 start_line 之前和 end_line 之后的代码
new_lines = lines[:start_line] + new_block + lines[end_line:]
file_path.write_text('\n'.join(new_lines), encoding="utf-8")

print(f"✅ 成功连根拔起并替换了第 {start_line+1} 行到第 {end_line} 行的损坏代码块")
print("👉 请重新运行: python apps/artforge/test_real_steps.py")