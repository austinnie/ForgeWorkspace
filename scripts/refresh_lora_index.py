# scripts/refresh_lora_index.py
"""强制重建 LoRA 索引缓存，确保 GUI 能正确扫描到模型"""
import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")
BASE_MODELS = Path(r"E:\SD_OpenVINO\models")

# 目标索引文件位置 (放在 sd_gui 的 scripts 目录下，与旧代码逻辑保持一致)
INDEX_DIR = WORKSPACE / "apps" / "sd_gui" / "scripts"
INDEX_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = INDEX_DIR / "lora_index.json"

loras = []
lora_dirs = {
    "sd15": BASE_MODELS / "sd15-lora",
    "sdxl": BASE_MODELS / "sdxl-lora"
}

print("🚀 开始扫描本地 LoRA 模型...\n")

for lora_type, lora_dir in lora_dirs.items():
    if not lora_dir.exists():
        print(f"⚠️ 目录不存在: {lora_dir}")
        continue
    
    print(f"🔍 扫描目录: {lora_dir}")
    count = 0
    for ext in [".safetensors", ".ckpt", ".pt"]:
        for filepath in lora_dir.glob(f"*{ext}"):
            name = filepath.stem
            size_mb = filepath.stat().st_size / (1024**2)
            
            loras.append({
                "name": name,
                "filename": filepath.name,
                "lora_type": lora_type,
                "lora_type_name": "SD1.5" if lora_type == "sd15" else "SDXL",
                "lora_type_icon": "🟢" if lora_type == "sd15" else "🔵",
                # 保留相对路径以兼容旧代码的 resolve_path 逻辑
                "path": f"../../models/{lora_type}-lora/{filepath.name}", 
                # 同时提供绝对路径作为兜底
                "absolute_path": str(filepath).replace("\\", "/"),
                "size_mb": round(size_mb, 2),
                "tags": ["uncategorized"],
                "score": 50,
                "version": None,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            })
            count += 1
    print(f"   ✅ 找到 {count} 个 {lora_type.upper()} LoRA")

# 构建完整的索引数据结构
index_data = {
    "project_root": str((WORKSPACE / "apps" / "sd_gui")).replace("\\", "/"),
    "lora_dirs": {k: str(v).replace("\\", "/") for k, v in lora_dirs.items()},
    "lora_dirs_relative": {
        "sd15": "../../models/sd15-lora",
        "sdxl": "../../models/sdxl-lora"
    },
    "total_loras": len(loras),
    "loras": loras,
    "default": loras[0]["name"] if loras else None,
    "default_type": "sd15"
}

# 写入文件
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index_data, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print(f"🎉 成功生成 LoRA 索引缓存!")
print(f"📁 保存路径: {INDEX_FILE}")
print(f"📊 共扫描到 {len(loras)} 个 LoRA 模型")
print("=" * 60)
print("\n👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")