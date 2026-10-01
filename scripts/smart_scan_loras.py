# scripts/smart_scan_loras.py
"""智能诊断并扫描 LoRA 模型，自动重建索引"""
import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")
CONFIG_FILE = WORKSPACE / "apps" / "sd_gui" / "data" / "configs" / "gui_config.json"
INDEX_FILE = WORKSPACE / "apps" / "sd_gui" / "scripts" / "lora_index.json"
BASE_MODELS = Path(r"E:\SD_OpenVINO\models")

print("🔍 正在诊断 LoRA 模型路径...\n")

# 1. 尝试从配置读取路径
lora_dirs_to_scan = []
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        lora_dirs_to_scan = config.get("paths", {}).get("lora_base_paths", [])
        print(f"📖 从配置读取到的 LoRA 路径: {lora_dirs_to_scan}")
else:
    print("⚠️ 未找到 gui_config.json，将使用默认路径")
    lora_dirs_to_scan = [str(BASE_MODELS / "sd15-lora"), str(BASE_MODELS / "sdxl-lora")]

# 2. 验证路径并收集文件
loras = []
valid_dirs = []

for dir_path_str in lora_dirs_to_scan:
    dir_path = Path(dir_path_str)
    if dir_path.exists() and dir_path.is_dir():
        valid_dirs.append(dir_path)
        print(f"✅ 找到目录: {dir_path}")
        count = 0
        for ext in [".safetensors", ".ckpt", ".pt"]:
            # 使用 rglob 递归扫描子目录
            for filepath in dir_path.rglob(f"*{ext}"):
                name = filepath.stem
                size_mb = filepath.stat().st_size / (1024**2)
                
                # 启发式判断：大小小于 700MB，或名字包含 lora/lyco
                is_lora_like = size_mb < 700 or "lora" in name.lower() or "lyco" in name.lower()
                
                if is_lora_like:
                    loras.append({
                        "name": name,
                        "filename": filepath.name,
                        "lora_type": "sd15" if "sd15" in str(dir_path).lower() else "sdxl",
                        "lora_type_name": "SD1.5" if "sd15" in str(dir_path).lower() else "SDXL",
                        "path": str(filepath.relative_to(BASE_MODELS)).replace("\\", "/"),
                        "absolute_path": str(filepath).replace("\\", "/"),
                        "size_mb": round(size_mb, 2),
                        "tags": ["auto_scanned"],
                        "score": 50,
                        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    })
                    count += 1
        print(f"   ↳ 扫描到 {count} 个疑似 LoRA 文件")
    else:
        print(f"❌ 目录不存在: {dir_path}")

# 3. 如果配置的路径都没找到，或者找到的太少，尝试全局扫描 BASE_MODELS
if not valid_dirs or len(loras) < 5:
    print("\n⚠️ 配置的路径未找到或文件过少，正在全局扫描 E:\\SD_OpenVINO\\models ...")
    global_count = 0
    for ext in [".safetensors", ".ckpt"]:
        for filepath in BASE_MODELS.rglob(f"*{ext}"):
            size_mb = filepath.stat().st_size / (1024**2)
            # 排除主模型 (通常 > 2GB)，只保留小模型或名字带 lora 的
            if size_mb < 700 or "lora" in filepath.name.lower() or "lyco" in filepath.name.lower():
                abs_path_str = str(filepath).replace("\\", "/")
                # 避免重复添加
                if not any(l["absolute_path"] == abs_path_str for l in loras):
                    loras.append({
                        "name": filepath.stem,
                        "filename": filepath.name,
                        "lora_type": "unknown",
                        "lora_type_name": "Unknown",
                        "path": str(filepath.relative_to(BASE_MODELS)).replace("\\", "/"),
                        "absolute_path": abs_path_str,
                        "size_mb": round(size_mb, 2),
                        "tags": ["global_scan"],
                        "score": 50,
                        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    })
                    global_count += 1
    print(f"✅ 全局扫描额外找到 {global_count} 个 LoRA 文件")

# 4. 保存索引
INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
index_data = {
    "project_root": str((WORKSPACE / "apps" / "sd_gui")).replace("\\", "/"),
    "lora_dirs": {str(d): str(d) for d in valid_dirs},
    "total_loras": len(loras),
    "loras": loras,
    "default": loras[0]["name"] if loras else None,
    "default_type": "sd15"
}

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index_data, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print(f"🎉 LoRA 索引重建完成!")
print(f"📁 保存路径: {INDEX_FILE}")
print(f"📊 共找到 {len(loras)} 个 LoRA 模型")
if len(loras) > 0:
    print(f"📋 前 3 个示例:")
    for l in loras[:3]:
        print(f"   - {l['name']} ({l['size_mb']} MB) -> {l['absolute_path']}")
else:
    print("⚠️ 未找到任何 LoRA 文件，请确认您的 LoRA 确实存放在 E:\\SD_OpenVINO\\models 目录下。")
print("=" * 60)
print("\n👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")