# scripts/fix_model_paths.py
"""修复 GUI 配置文件中的模型路径，使其指向正确的 E:\SD_OpenVINO\models 目录"""
import json
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")
BASE_MODELS = r"E:\SD_OpenVINO\models"

# 1. 修复 gui_config.json
gui_config_path = WORKSPACE / "apps" / "sd_gui" / "data" / "configs" / "gui_config.json"
if gui_config_path.exists():
    with open(gui_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if "paths" in config:
        config["paths"]["model_base_paths"] = [
            rf"{BASE_MODELS}\sd-v1-5",
            rf"{BASE_MODELS}\sdxl"
        ]
        config["paths"]["lora_base_paths"] = [
            rf"{BASE_MODELS}\sd15-lora",
            rf"{BASE_MODELS}\sdxl-lora"
        ]
        config["paths"]["vae_base_paths"] = [
            rf"{BASE_MODELS}\vae"
        ]
        
    with open(gui_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✅ 已修复: gui_config.json 的模型/LoRA/VAE 路径")
else:
    print("⚠️ 未找到 gui_config.json")

# 2. 修复 janus_config.json
janus_config_path = WORKSPACE / "apps" / "sd_gui" / "data" / "configs" / "janus_config.json"
if janus_config_path.exists():
    with open(janus_config_path, 'r', encoding='utf-8') as f:
        j_config = json.load(f)
    
    if "janus" in j_config:
        j_config["janus"]["model_1b_path"] = rf"{BASE_MODELS}\janus\janus-pro-1b"
        j_config["janus"]["model_7b_path"] = rf"{BASE_MODELS}\janus\janus-pro-7b"
        
    with open(janus_config_path, 'w', encoding='utf-8') as f:
        json.dump(j_config, f, indent=2, ensure_ascii=False)
    print("✅ 已修复: janus_config.json 的 Janus 模型路径")
else:
    print("⚠️ 未找到 janus_config.json")

print("\n🎉 路径修复完毕！")
print("👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")