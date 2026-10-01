# scripts/diagnose_and_fix_lora.py
"""终极诊断：扫描真实 LoRA 路径并自动修复配置"""
import os
import json
from pathlib import Path
from datetime import datetime

BASE_MODELS = Path(r"E:\SD_OpenVINO\models")
WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

print("=" * 60)
print(f"🔍 正在扫描 {BASE_MODELS} 目录结构...")
print("=" * 60)

if not BASE_MODELS.exists():
    print(f"❌ 目录不存在: {BASE_MODELS}")
    print("💡 请确认您的模型是否确实放在 E:\\SD_OpenVINO\\models 下？")
    exit(1)

# 1. 打印顶层目录结构，帮助诊断
print("\n📂 E:\\SD_OpenVINO\\models 下的顶层文件夹:")
for item in BASE_MODELS.iterdir():
    if item.is_dir():
        print(f"  - {item.name}/")

# 2. 智能寻找疑似 LoRA 的文件
loras_found = []
print("\n⏳ 正在递归扫描所有 .safetensors / .ckpt / .pt 文件...")
for ext in [".safetensors", ".ckpt", ".pt"]:
    for filepath in BASE_MODELS.rglob(f"*{ext}"):
        size_mb = filepath.stat().st_size / (1024**2)
        name_lower = filepath.name.lower()
        
        # 启发式判断：大小 < 700MB，或者名字里明确包含 lora/lyco
        is_lora_like = (size_mb < 700) or ("lora" in name_lower) or ("lyco" in name_lower)
        
        # 排除明显的大体积底模 (通常 > 2GB)
        if size_mb > 2000 and not is_lora_like:
            continue
            
        if is_lora_like:
            loras_found.append(filepath)

print(f"\n✅ 扫描完成！共找到 {len(loras_found)} 个疑似 LoRA 文件。")

if loras_found:
    print("\n📋 前 5 个 LoRA 示例:")
    for f in loras_found[:5]:
        print(f"  - {f.relative_to(BASE_MODELS)}  ({f.stat().st_size / 1024**2:.1f} MB)")
    
    # 3. 提取它们实际所在的父目录
    lora_dirs = list(set([str(f.parent) for f in loras_found]))
    print(f"\n📁 这些 LoRA 实际存放在以下 {len(lora_dirs)} 个目录中:")
    for d in lora_dirs:
        print(f"  - {d}")
    
    # 4. 自动修复 gui_config.json
    config_path = WORKSPACE / "apps" / "sd_gui" / "data" / "configs" / "gui_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "paths" not in config:
            config["paths"] = {}
        config["paths"]["lora_base_paths"] = lora_dirs
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 已自动更新 gui_config.json 中的 lora_base_paths")
    else:
        print(f"\n⚠️ 未找到 gui_config.json")

    # 5. 强制生成最新的 lora_index.json (GUI 启动时读取此文件)
    index_data = {
        "project_root": str((WORKSPACE / "apps" / "sd_gui")),
        "lora_dirs": {f"dir_{i}": d for i, d in enumerate(lora_dirs)},
        "total_loras": len(loras_found),
        "loras": [{
            "name": f.stem,
            "filename": f.name,
            "lora_type": "sd15" if "sd-v1-5" in str(f).lower() or "sd15" in str(f).lower() else "sdxl",
            "lora_type_name": "SD1.5" if "sd-v1-5" in str(f).lower() or "sd15" in str(f).lower() else "SDXL",
            "path": str(f.relative_to(BASE_MODELS)).replace("\\", "/"),
            "absolute_path": str(f).replace("\\", "/"),
            "size_mb": round(f.stat().st_size / (1024**2), 2),
            "tags": ["auto_scanned"],
            "score": 50,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        } for f in loras_found],
        "default": loras_found[0].stem if loras_found else None,
        "default_type": "sd15"
    }
    
    index_path = WORKSPACE / "apps" / "sd_gui" / "scripts" / "lora_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    print(f"✅ 已生成最新的 lora_index.json (包含 {len(loras_found)} 个模型)")
    
else:
    print("\n⚠️ 在 E:\\SD_OpenVINO\\models 下没有找到任何疑似 LoRA 的文件。")
    print("💡 请确认：")
    print("   1. 您的 LoRA 文件是否确实放在了 E:\\SD_OpenVINO\\models 目录下？")
    print("   2. 或者它们被放在了其他盘符/文件夹（例如 D:\\models）？")
    print("   3. 文件扩展名是否为 .safetensors 或 .ckpt？")

print("\n" + "=" * 60)
print("👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")
print("=" * 60)