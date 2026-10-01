# scripts/check_controlnet_models.py
"""
ControlNet 模型检查工具 v2 - 全面搜索
扫描所有缓存目录，检查：
  1. ControlNet 主模型 (支持 .safetensors / .bin / .pt)
  2. Annotators 预处理器模型
  3. 统计完整/不完整/缺失的模型
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ==================== 配置 ====================
# 多个可能的缓存目录
CACHE_DIRS = [
    r"E:\hf_cache\.cache\hub",
    r"E:\hf_cache\.cache",
    r"C:\Users\user\.cache\huggingface\hub",
    r"C:\Users\user\.cache\huggingface",
    r"C:\Users\user\.cache",
    r"E:\SD_OpenVINO\sd_generator\cache",
    r"E:\SD_OpenVINO\Markflow_4image\skills\controlnet\cache",
    r"E:\SD_OpenVINO\Markflow_4image\cache",
    # Python site-packages
    r"C:\Users\user\AppData\Roaming\Python\Python314\site-packages\controlnet_aux",
    r"C:\Users\user\AppData\Local\Programs\Python\Python314\Lib\site-packages\controlnet_aux",
]

# ControlNet 模型列表 (支持多种文件格式)
CONTROLNET_MODELS = {
    "canny": {
        "repos": [
            "lllyasviel/sd-controlnet-canny",
            "lllyasviel/control_v11p_sd15_canny",
        ],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "openpose": {
        "repos": [
            "lllyasviel/sd-controlnet-openpose",
            "lllyasviel/control_v11p_sd15_openpose",
        ],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "depth": {
        "repos": ["lllyasviel/sd-controlnet-depth"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "hed": {
        "repos": ["lllyasviel/sd-controlnet-hed"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "lineart": {
        "repos": ["lllyasviel/control_v11p_sd15_lineart"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "normal": {
        "repos": ["lllyasviel/sd-controlnet-normal"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "mlsd": {
        "repos": ["lllyasviel/sd-controlnet-mlsd"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "seg": {
        "repos": ["lllyasviel/sd-controlnet-seg"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
    "scribble": {
        "repos": ["lllyasviel/sd-controlnet-scribble"],
        "files": ["diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.bin", "pytorch_model.bin"],
        "min_size_mb": 500,
    },
}

# Annotators 预处理器模型
ANNOTATOR_MODELS = {
    "body_pose_model.pth": {"size_mb": 204, "desc": "OpenPose 身体姿态"},
    "hand_pose_model.pth": {"size_mb": 144, "desc": "OpenPose 手部姿态"},
    "facenet.pth": {"size_mb": 150, "desc": "人脸检测"},
    "dpt_hybrid-midas-501f0c75.pt": {"size_mb": 481, "desc": "Midas 深度估计"},
    "ControlNetHED.pth": {"size_mb": 29, "desc": "HED 边缘检测"},
    "mlsd_large_512_fp32.pth": {"size_mb": 6, "desc": "MLSD 直线检测"},
    "scannet.pth": {"size_mb": 284, "desc": "ScanNet 场景分割"},
    "sk_model.pth": {"size_mb": 17, "desc": "Sketch 模型"},
    "sk_model2.pth": {"size_mb": 17, "desc": "Sketch 模型 v2"},
}


def get_repo_folder(repo_id: str) -> str:
    """将 repo_id 转换为缓存文件夹名"""
    return f"models--{repo_id.replace('/', '--')}"


def find_snapshots(repo_path: Path) -> List[Path]:
    """查找 repo 文件夹下的所有 snapshot 目录"""
    if not repo_path.exists():
        return []
    
    snapshots = []
    for item in repo_path.iterdir():
        if item.is_dir() and item.name.startswith("snapshots"):
            for sub in item.iterdir():
                if sub.is_dir():
                    snapshots.append(sub)
        elif item.is_dir() and len(item.name) == 40 and item.name.isalnum():
            snapshots.append(item)
    return snapshots


def check_controlnet_model(repo_path: Path, file_names: List[str], min_size_mb: float) -> Tuple[str, float, str, str]:
    """检查 ControlNet 主模型 (支持多种文件格式)"""
    snapshots = find_snapshots(repo_path)
    if not snapshots:
        return "not_found", 0, "", ""
    
    # 取最新的 snapshot
    latest = max(snapshots, key=lambda p: p.stat().st_mtime)
    
    # 尝试所有可能的文件名
    for file_name in file_names:
        model_file = latest / file_name
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024**2)
            if size_mb >= min_size_mb:
                return "complete", size_mb, str(latest), file_name
            else:
                return "partial", size_mb, str(latest), file_name
    
    return "no_file", 0, str(latest), ""


def find_any_model(cache_path: Path, model_name: str, model_info: Dict) -> Tuple[str, float, str, str]:
    """在缓存目录中查找任意 ControlNet 模型"""
    # 尝试所有可能的 repo
    for repo_id in model_info["repos"]:
        repo_folder = get_repo_folder(repo_id)
        repo_path = cache_path / repo_folder
        if repo_path.exists():
            status, size_mb, snapshot_path, file_name = check_controlnet_model(
                repo_path, model_info["files"], model_info["min_size_mb"]
            )
            if status != "not_found":
                return status, size_mb, snapshot_path, file_name
    
    return "not_found", 0, "", ""


def check_annotators(snapshot_path: Path) -> Dict:
    """检查 Annotators 预处理器模型"""
    result = {}
    for name, info in ANNOTATOR_MODELS.items():
        file_path = snapshot_path / name
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024**2)
            result[name] = {
                "exists": True,
                "size_mb": round(size_mb, 2),
                "expected_mb": info["size_mb"],
                "desc": info["desc"],
            }
        else:
            result[name] = {"exists": False, "expected_mb": info["size_mb"], "desc": info["desc"]}
    return result


def find_annotators(cache_path: Path) -> Optional[Path]:
    """查找 Annotators 目录"""
    candidates = [
        cache_path / "models--lllyasviel--Annotators",
        cache_path / "models--llyasviel--Annotators",
    ]
    
    for cand in candidates:
        if cand.exists():
            snapshots = find_snapshots(cand)
            if snapshots:
                return max(snapshots, key=lambda p: p.stat().st_mtime)
    return None


def scan_cache_dir(cache_path: Path) -> Dict:
    """扫描单个缓存目录"""
    result = {
        "path": str(cache_path),
        "exists": cache_path.exists(),
        "controlnet": {},
        "annotators": {},
        "annotators_path": None,
    }
    
    if not cache_path.exists():
        return result
    
    # 1. 检查 ControlNet 主模型 (支持多种格式)
    for name, info in CONTROLNET_MODELS.items():
        status, size_mb, snapshot_path, file_name = find_any_model(cache_path, name, info)
        result["controlnet"][name] = {
            "status": status,
            "size_mb": round(size_mb, 1),
            "snapshot": snapshot_path,
            "file": file_name,
        }
    
    # 2. 检查 Annotators 预处理器
    annotators_path = find_annotators(cache_path)
    if annotators_path:
        result["annotators_path"] = str(annotators_path)
        result["annotators"] = check_annotators(annotators_path)
    
    return result


def print_results(results: List[Dict]):
    """打印检查结果"""
    print("=" * 90)
    print("📊 ControlNet 模型完整检查 v2")
    print("=" * 90)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 汇总统计
    all_complete = set()
    all_partial = set()
    all_annotators = False
    found_in = {}
    
    for result in results:
        if not result["exists"]:
            continue
        
        print(f"📁 {result['path']}")
        print("-" * 90)
        
        # ControlNet 主模型
        for name, info in result["controlnet"].items():
            status = info["status"]
            size = info["size_mb"]
            file_name = info.get("file", "")
            
            if status == "complete":
                icon = "✅"
                all_complete.add(name)
                found_in[name] = found_in.get(name, 0) + 1
            elif status == "partial":
                icon = "⚠️"
                all_partial.add(name)
            elif status == "no_file":
                icon = "📁"
            else:
                icon = "❌"
            
            file_info = f" ({file_name})" if file_name else ""
            print(f"   {icon} {name:<12} {status:<12} {size:>6.1f}MB  {file_info}")
        
        # Annotators
        if result["annotators"]:
            all_annotators = True
            print(f"\n   📦 Annotators 预处理器 ({result['annotators_path']}):")
            for name, info in result["annotators"].items():
                if info["exists"]:
                    status = "✅"
                    size = info["size_mb"]
                    desc = info["desc"]
                    print(f"      {status} {name:<30} {size:>6.1f}MB  {desc}")
                else:
                    status = "❌"
                    desc = info["desc"]
                    print(f"      {status} {name:<30} {'':>6}    {desc}")
        
        print()
    
    # 总结
    print("=" * 90)
    print("📊 总结")
    print("-" * 90)
    
    if all_complete:
        print(f"✅ 完整 ControlNet 模型: {', '.join(sorted(all_complete))}")
        print(f"\n📂 模型位置:")
        for name in sorted(all_complete):
            count = found_in.get(name, 0)
            print(f"   {name}: {count} 个位置")
    else:
        print("❌ 没有完整的 ControlNet 模型")
    
    if all_partial:
        print(f"⚠️ 部分下载 (不完整): {', '.join(sorted(all_partial))}")
    
    print(f"📦 Annotators 预处理器: {'✅ 已安装' if all_annotators else '❌ 未安装'}")
    
    # 推荐可用的模型
    if all_complete:
        print(f"\n💡 可直接使用的 ControlNet 模型:")
        for name in sorted(all_complete):
            print(f"   python cli.py bird_sketch -i test.jpg --controlnet {name} -n 1 --steps 10")
    else:
        print("\n💡 没有完整的 ControlNet 模型，请运行以下命令下载:")
        print("   python cli.py bird_sketch -i test.jpg --controlnet openpose -n 1")
    
    print("=" * 90)


def main():
    all_results = []
    
    for cache_dir in CACHE_DIRS:
        result = scan_cache_dir(Path(cache_dir))
        all_results.append(result)
    
    print_results(all_results)


if __name__ == "__main__":
    main()