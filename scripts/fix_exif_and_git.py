# scripts/fix_exif_and_git.py
"""修复 EXIF 注入器的旧依赖 + 生成完善的 .gitignore"""
from pathlib import Path

ROOT = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# ============================================================
# 修复 1: exif_injector.py 中的 utils.logger 依赖
# ============================================================
exif_file = ROOT / "forgecore" / "forgecore" / "image" / "exif_injector.py"
if exif_file.exists():
    content = exif_file.read_text(encoding="utf-8")
    
    # 替换旧的 logger 导入
    old_imports = [
        "from utils.logger import",
        "from utils import logger",
        "import utils.logger",
    ]
    
    modified = False
    for old in old_imports:
        if old in content:
            content = content.replace(old, "# [ForgeCore] 旧依赖已移除\n# " + old)
            modified = True
    
    # 如果没有 logger 定义，添加一个简易版
    if "logger" in content and "import logging" not in content:
        # 在文件开头添加 logging
        content = "import logging\nlogger = logging.getLogger('forgecore.image.exif')\n" + content
        modified = True
    
    if modified:
        exif_file.write_text(content, encoding="utf-8")
        print(f"✅ 修复 1: exif_injector.py 的 utils.logger 依赖已清理")
    else:
        print(f"ℹ️ 修复 1: exif_injector.py 无需修改（可能结构不同）")
else:
    print(f"⚠️ 未找到 exif_injector.py")

# ============================================================
# 修复 2: 生成完善的 .gitignore
# ============================================================
gitignore = ROOT / ".gitignore"
gitignore_content = """# ============================================================
# ForgeWorkspace .gitignore
# ============================================================

# --- 运行时输出 (绝对不提交) ---
output/
apps/*/output/
temp_gather/
*.png
*.jpg
*.jpeg
*.webp
*.gif
*.mp4

# 保留 .gitkeep (用于保持空目录结构)
!apps/*/.gitkeep
!**/.gitkeep

# --- 敏感配置 (绝对不提交 API Key!) ---
.env
.env.local
*.local.json

# --- Python 缓存 ---
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# --- 虚拟环境 ---
venv/
.venv/
env/
ENV/

# --- IDE ---
.vscode/
.idea/
*.swp
*.swo
*~

# --- 系统垃圾 ---
.DS_Store
Thumbs.db
desktop.ini

# --- AI 模型文件 (太大) ---
*.safetensors
*.ckpt
*.bin
*.pth
*.onnx

# --- 日志 ---
*.log
*.tmp
*.bak

# --- 代码收集工具输出 ---
project_snapshot_*.txt
project_code_dump.txt
"""

gitignore.write_text(gitignore_content.strip(), encoding="utf-8")
print(f"✅ 修复 2: .gitignore 已生成")

# ============================================================
# 修复 3: 在 apps 各 output 目录放 .gitkeep
# ============================================================
for app in ["artforge", "layerforge", "promptforge", "sd_gui"]:
    out_dir = ROOT / "apps" / app / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = out_dir / ".gitkeep"
    gitkeep.touch()
    
print(f"✅ 修复 3: 各 App 的 output/.gitkeep 已创建")

print("\n🎉 所有修复完成！现在可以安全提交 Git 了。")