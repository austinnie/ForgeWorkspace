# scripts/fix_lora_index_paths.py
"""修正 lora_index.json 的路径基准，使其能被旧版 GUI 正确解析"""
import json
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")
INDEX_FILE = WORKSPACE / "apps" / "sd_gui" / "scripts" / "lora_index.json"
BASE_MODELS = Path(r"E:\SD_OpenVINO\models")
BASE_ROOT = Path(r"E:\SD_OpenVINO")

if not INDEX_FILE.exists():
    print("❌ 未找到 lora_index.json，请先运行 diagnose_and_fix_lora.py")
    exit(1)

print("🔧 正在修正 lora_index.json 的路径基准...\n")

with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. 修正 project_root 为 E:\SD_OpenVINO
data["project_root"] = str(BASE_ROOT).replace("\\", "/")
print(f"✅ 更新 project_root 为: {data['project_root']}")

# 2. 修正每个 LoRA 的 path，使其相对于 E:\SD_OpenVINO
valid_loras = []
for lora in data["loras"]:
    abs_path = Path(lora["absolute_path"])
    try:
        # 计算相对于 E:\SD_OpenVINO 的路径，例如: models/sd15-lora/xxx.safetensors
        rel_path = abs_path.relative_to(BASE_ROOT).as_posix()
        lora["path"] = rel_path
        valid_loras.append(lora)
    except ValueError:
        # 如果不在 E:\SD_OpenVINO 下，保留绝对路径
        lora["path"] = lora["absolute_path"]
        valid_loras.append(lora)

data["loras"] = valid_loras
data["total_loras"] = len(valid_loras)

# 3. 同时更新 gui_config.json 中的路径，确保一致性
config_path = WORKSPACE / "apps" / "sd_gui" / "data" / "configs" / "gui_config.json"
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 将路径改为相对于 E:\SD_OpenVINO 的形式，或者直接保留绝对路径（旧代码通常能处理绝对路径）
    # 为了最安全，我们直接写入绝对路径
    lora_dirs = [
        str(BASE_MODELS / "sd15-lora"),
        str(BASE_MODELS / "sdxl-lora")
    ]
    if "paths" not in config:
        config["paths"] = {}
    config["paths"]["lora_base_paths"] = lora_dirs
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✅ 已同步更新 gui_config.json")

# 4. 保存修正后的索引
with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n🎉 路径基准修正完成！")
print(f"📊 有效 LoRA 数量: {len(valid_loras)}")
if valid_loras:
    print(f"📋 路径示例:")
    print(f"   project_root: {data['project_root']}")
    print(f"   lora path:    {valid_loras[0]['path']}")
    print(f"   拼接后应为:   {data['project_root']}/{valid_loras[0]['path']}")

print("\n👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")