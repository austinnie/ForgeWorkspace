# scripts/collect_controlnet_models.py
"""
收集完整的 ControlNet 模型到统一目录
只保留一份，避免重复
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# ==================== 配置 ====================
# 目标目录（统一存放模型）
TARGET_DIR = Path(r"E:\SD_OpenVINO\models\controlnet")

# 源目录（搜索模型的地方）
SOURCE_DIRS = [
    Path(r"E:\hf_cache\.cache\hub"),
    Path(r"C:\Users\user\.cache\huggingface\hub"),
    Path(r"C:\Users\user\.cache"),
    Path(r"E:\SD_OpenVINO\sd_generator\cache"),
    Path(r"E:\SD_OpenVINO\Markflow_4image\cache"),
]

# 模型映射：目标文件名 -> 源文件夹名
MODEL_MAPPING = {
    "openpose": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-openpose",
            "models--lllyasviel--control_v11p_sd15_openpose",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.5,
    },
    "lineart": {
        "source_folders": [
            "models--lllyasviel--control_v11p_sd15_lineart",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.5,
    },
    "seg": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-seg",
            "models--CIDAS--clipseg-rd64-refined",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.3,
    },
    "canny": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-canny",
            "models--lllyasviel--control_v11p_sd15_canny",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.5,
    },
    "depth": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-depth",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.3,
    },
    "hed": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-hed",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.3,
    },
    "normal": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-normal",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.3,
    },
    "mlsd": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-mlsd",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.3,
    },
    "scribble": {
        "source_folders": [
            "models--lllyasviel--sd-controlnet-scribble",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.3,
    },
    "openpose_full": {
        "source_folders": [
            "models--lllyasviel--control_v11p_sd15_openpose",
        ],
        "file_pattern": "*.safetensors",
        "min_size_gb": 0.5,
    },
}


def find_model_file(source_dir: Path, folder_names: list, file_pattern: str, min_size_gb: float) -> tuple:
    """在源目录中查找模型文件，返回 (文件路径, 大小GB, 源文件夹名)"""
    for folder_name in folder_names:
        folder_path = source_dir / folder_name
        if not folder_path.exists():
            continue
        
        # 查找 snapshot 目录
        snapshots = list(folder_path.glob("snapshots/*"))
        if snapshots:
            # 取最新的 snapshot
            latest = max(snapshots, key=lambda p: p.stat().st_mtime)
            for f in latest.glob(file_pattern):
                size_gb = f.stat().st_size / (1024**3)
                if size_gb >= min_size_gb:
                    return f, size_gb, folder_name
        
        # 直接查找（非 snapshot 结构）
        for f in folder_path.glob(file_pattern):
            size_gb = f.stat().st_size / (1024**3)
            if size_gb >= min_size_gb:
                return f, size_gb, folder_name
        
        # 查找子目录中的文件
        for sub in folder_path.iterdir():
            if sub.is_dir():
                for f in sub.glob(file_pattern):
                    size_gb = f.stat().st_size / (1024**3)
                    if size_gb >= min_size_gb:
                        return f, size_gb, folder_name
    
    return None, 0, ""


def collect_models():
    """收集所有模型到统一目录"""
    print("=" * 90)
    print("📦 ControlNet 模型收集工具")
    print("=" * 90)
    print(f"目标目录: {TARGET_DIR}")
    print()
    
    # 创建目标目录
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    collected = {}
    skipped = {}
    errors = {}
    
    for model_name, config in MODEL_MAPPING.items():
        print(f"🔍 查找 {model_name}...")
        
        found = False
        for source_dir in SOURCE_DIRS:
            if not source_dir.exists():
                continue
            
            file_path, size_gb, source_folder = find_model_file(
                source_dir,
                config["source_folders"],
                config["file_pattern"],
                config["min_size_gb"]
            )
            
            if file_path:
                # 确定目标文件名
                target_file = TARGET_DIR / f"{model_name}.safetensors"
                
                # 检查目标是否已存在且大小相同
                if target_file.exists():
                    existing_size = target_file.stat().st_size / (1024**3)
                    if abs(existing_size - size_gb) < 0.01:
                        print(f"   ✅ {model_name} 已存在，跳过 ({size_gb:.2f}GB)")
                        collected[model_name] = {
                            "source": str(file_path),
                            "target": str(target_file),
                            "size_gb": size_gb,
                            "status": "exists",
                        }
                        found = True
                        break
                
                try:
                    # 复制文件
                    shutil.copy2(file_path, target_file)
                    print(f"   ✅ {model_name} 复制完成 ({size_gb:.2f}GB)")
                    collected[model_name] = {
                        "source": str(file_path),
                        "target": str(target_file),
                        "size_gb": size_gb,
                        "status": "copied",
                    }
                    found = True
                    break
                except Exception as e:
                    print(f"   ❌ {model_name} 复制失败: {e}")
                    errors[model_name] = str(e)
                    break
        
        if not found:
            print(f"   ❌ {model_name} 未找到完整模型")
            skipped[model_name] = "未找到"
    
    # 打印总结
    print("\n" + "=" * 90)
    print("📊 收集总结")
    print("=" * 90)
    
    print(f"\n✅ 已收集: {len(collected)} 个模型")
    for name, info in collected.items():
        status = "已存在" if info["status"] == "exists" else "已复制"
        print(f"   {name}: {status} ({info['size_gb']:.2f}GB)")
    
    if skipped:
        print(f"\n❌ 未找到: {len(skipped)} 个模型")
        for name in skipped:
            print(f"   {name}: 未找到")
    
    if errors:
        print(f"\n⚠️ 错误: {len(errors)} 个")
        for name, err in errors.items():
            print(f"   {name}: {err}")
    
    # 保存清单
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "target_dir": str(TARGET_DIR),
        "collected": collected,
        "skipped": skipped,
        "errors": errors,
    }
    
    manifest_file = TARGET_DIR / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n📄 清单已保存: {manifest_file}")
    
    # 列出目标目录内容
    print(f"\n📂 目标目录内容:")
    for f in sorted(TARGET_DIR.glob("*.safetensors")):
        size_gb = f.stat().st_size / (1024**3)
        print(f"   {f.name} ({size_gb:.2f}GB)")


def main():
    collect_models()


if __name__ == "__main__":
    main()