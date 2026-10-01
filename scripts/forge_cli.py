#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Forge CLI - 全局开发者工具 (安全重构版)"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 定位到 ForgeWorkspace 根目录
ROOT_DIR = Path(__file__).resolve().parent.parent

# 🔥 核心：必须排除的大体积目录
IGNORE_DIRS = {
    ".git", "venv", ".venv", "env", "node_modules", 
    "__pycache__", ".idea", ".vscode",
    "models", "data", "shared_assets", "output", "outputs", 
    "build", "dist", "temp_gather", "logs"
}

# 必须排除的文件扩展名 (模型、媒体、字体、二进制)
IGNORE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".log", ".tmp", ".db", ".sqlite",
    ".safetensors", ".ckpt", ".pt", ".bin", ".onnx", 
    ".ttf", ".otf", ".ttc", ".fon", 
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", 
    ".mp4", ".mp3", ".wav", ".zip", ".rar", ".7z"
}

def gather_code():
    """一键收集所有干净代码 (安全版：绝对不会打包模型和大文件)"""
    print("🚀 开始收集 ForgeWorkspace 干净代码 (安全模式)...\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"ForgeWorkspace_CodeOnly_{timestamp}"
    temp_dir = ROOT_DIR / "temp_gather" / zip_name
    
    print(f"📂 目标目录: {temp_dir}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    file_count = 0
    skipped_large = 0

    # 手动遍历，比 shutil.copytree 更安全可控
    for root, dirs, files in os.walk(ROOT_DIR):
        # 1. 原地修改 dirs，阻止 os.walk 进入被排除的目录 (如 models)
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            
            # 2. 排除特定扩展名
            if file_path.suffix.lower() in IGNORE_EXTS:
                continue
                
            # 3. 双重保险：检查文件大小 (超过 1MB 的文件直接跳过)
            try:
                if file_path.stat().st_size > 1024 * 1024: # 1MB
                    skipped_large += 1
                    continue
            except OSError:
                continue

            # 4. 计算相对路径并复制
            try:
                rel_path = file_path.relative_to(ROOT_DIR)
                dest_path = temp_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                file_count += 1
            except Exception as e:
                print(f"⚠️ 复制失败 {file_path.name}: {e}")

    print(f"\n✅ 收集完成！")
    print(f"📊 共打包 {file_count} 个代码/文本文件")
    print(f" 自动跳过了 {skipped_large} 个大文件/媒体/模型文件")
    print(f"📁 安全路径: {temp_dir}")
    print(f"💡 提示：现在您可以放心地将此目录压缩为 .zip，体积应该只有几 MB。")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gather":
        gather_code()
    else:
        print("用法: python scripts/forge_cli.py gather")