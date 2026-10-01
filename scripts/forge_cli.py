# scripts/forge_cli.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Forge CLI - 全局开发者工具"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 定位到 ForgeWorkspace 根目录
ROOT_DIR = Path(__file__).resolve().parent.parent

# 需要排除的文件和目录
IGNORE_PATTERNS = [
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    ".git", ".env", ".env.*", "venv", ".venv", "env",
    "output", "outputs", "*.log", "*.tmp",
    ".idea", ".vscode", "node_modules"
]

def gather_code():
    """一键收集所有干净代码"""
    print("🚀 开始收集 ForgeWorkspace 干净代码...\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"ForgeWorkspace_Snapshot_{timestamp}"
    temp_dir = ROOT_DIR / "temp_gather" / zip_name
    
    print(f"📂 目标目录: {temp_dir}")
    
    # 复制整个工作区，但忽略指定模式
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        
    shutil.copytree(
        ROOT_DIR, 
        temp_dir, 
        ignore=shutil.ignore_patterns(*IGNORE_PATTERNS)
    )
    
    # 统计文件
    py_files = list(temp_dir.rglob("*.py"))
    print(f"\n✅ 收集完成！")
    print(f"📊 共打包 {len(py_files)} 个 Python 文件")
    print(f"📁 临时路径: {temp_dir}")
    print(f"💡 提示：您可以手动将此目录压缩为 .zip 备份，或发送给 AI 辅助分析。")
    
    # 可选：自动清理临时目录 (取消注释下一行以启用)
    # shutil.rmtree(temp_dir)
    # print("🧹 临时文件已自动清理。")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gather":
        gather_code()
    else:
        print("用法: python scripts/forge_cli.py gather")