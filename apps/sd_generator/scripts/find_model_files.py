# scripts/find_model_files.py
"""
全面搜索 ControlNet 模型文件 v3
支持多种文件格式，按模型类型分组显示
"""

import os
from pathlib import Path
from datetime import datetime
import argparse
import json

# ==================== 配置 ====================
# 要搜索的文件扩展名
SEARCH_EXTS = ['.safetensors', '.bin', '.pt', '.pth', '.ckpt', '.onnx', '.pb']

# 最小文件大小 (MB)
MIN_SIZE_MB = 10

# ==================== 所有可能的缓存目录 ====================
SEARCH_DIRS = [
    # HuggingFace 默认缓存
    r"C:\Users\user\.cache\huggingface\hub",
    r"C:\Users\user\.cache\huggingface",
    r"C:\Users\user\.cache",
    # 项目缓存
    r"E:\hf_cache\.cache\hub",
    r"E:\hf_cache\.cache",
    r"E:\SD_OpenVINO\sd_generator\cache",
    r"E:\SD_OpenVINO\Markflow_4image\skills\controlnet\cache",
    r"E:\SD_OpenVINO\Markflow_4image\cache",
    # Markflow 根目录 (可能有模型)
    r"E:\SD_OpenVINO\Markflow_4image",
    # 完整版 ControlNet
    r"E:\SD_OpenVINO\controlnet",
    r"E:\SD_OpenVINO\controlnet\models",
    # Python site-packages
    r"C:\Users\user\AppData\Roaming\Python\Python314\site-packages\controlnet_aux",
    r"C:\Users\user\AppData\Local\Programs\Python\Python314\Lib\site-packages\controlnet_aux",
    # 模型目录
    r"E:\SD_OpenVINO\models",
]

# ControlNet 模型配置
MODEL_TYPES = {
    'canny': {
        'keywords': ['canny', 'control_v11p_sd15_canny', 'sd-controlnet-canny'],
        'repo': 'lllyasviel/sd-controlnet-canny',
        'min_size_gb': 0.5,
        'cache_folder': 'models--lllyasviel--sd-controlnet-canny',
    },
    'openpose': {
        'keywords': ['openpose', 'control_v11p_sd15_openpose', 'sd-controlnet-openpose', 'open_pose'],
        'repo': 'lllyasviel/sd-controlnet-openpose',
        'min_size_gb': 0.5,
        'cache_folder': 'models--lllyasviel--sd-controlnet-openpose',
    },
    'depth': {
        'keywords': ['depth', 'midas', 'dpt_hybrid', 'sd-controlnet-depth'],
        'repo': 'lllyasviel/sd-controlnet-depth',
        'min_size_gb': 0.1,
        'cache_folder': 'models--lllyasviel--sd-controlnet-depth',
    },
    'hed': {
        'keywords': ['hed', 'ControlNetHED', 'softedge', 'sd-controlnet-hed'],
        'repo': 'lllyasviel/sd-controlnet-hed',
        'min_size_gb': 0.1,
        'cache_folder': 'models--lllyasviel--sd-controlnet-hed',
    },
    'lineart': {
        'keywords': ['lineart', 'control_v11p_sd15_lineart', 'sd-controlnet-lineart'],
        'repo': 'lllyasviel/control_v11p_sd15_lineart',
        'min_size_gb': 0.5,
        'cache_folder': 'models--lllyasviel--control_v11p_sd15_lineart',
    },
    'normal': {
        'keywords': ['normal', 'normalbae', 'sd-controlnet-normal'],
        'repo': 'lllyasviel/sd-controlnet-normal',
        'min_size_gb': 0.1,
        'cache_folder': 'models--lllyasviel--sd-controlnet-normal',
    },
    'mlsd': {
        'keywords': ['mlsd', 'mlsd_large', 'sd-controlnet-mlsd'],
        'repo': 'lllyasviel/sd-controlnet-mlsd',
        'min_size_gb': 0.1,
        'cache_folder': 'models--lllyasviel--sd-controlnet-mlsd',
    },
    'seg': {
        'keywords': ['seg', 'uniformer', 'segmentation', 'sd-controlnet-seg'],
        'repo': 'lllyasviel/sd-controlnet-seg',
        'min_size_gb': 0.3,
        'cache_folder': 'models--lllyasviel--sd-controlnet-seg',
    },
    'scribble': {
        'keywords': ['scribble', 'sd-controlnet-scribble'],
        'repo': 'lllyasviel/sd-controlnet-scribble',
        'min_size_gb': 0.3,
        'cache_folder': 'models--lllyasviel--sd-controlnet-scribble',
    },
    'openpose_full': {
        'keywords': ['control_v11p_sd15_openpose', 'openpose_full'],
        'repo': 'lllyasviel/control_v11p_sd15_openpose',
        'min_size_gb': 0.5,
        'cache_folder': 'models--lllyasviel--control_v11p_sd15_openpose',
    },
}


def identify_model_type(file_path: str, file_name: str) -> tuple:
    """根据文件名和路径识别模型类型，返回 (类型, 是否确定)"""
    name_lower = file_name.lower()
    path_lower = file_path.lower()
    
    # 先检查是否匹配已知模型
    for model_type, info in MODEL_TYPES.items():
        for kw in info['keywords']:
            if kw in name_lower or kw in path_lower:
                return model_type, True
    
    # 检查是否是 Annotators 预处理器
    annotator_keywords = ['body_pose', 'hand_pose', 'facenet', 'dpt_hybrid', 'upernet', 'scannet']
    for kw in annotator_keywords:
        if kw in name_lower:
            return 'annotator', True
    
    # 检查是否是通用 controlnet 文件
    if 'controlnet' in name_lower or 'controlnet' in path_lower:
        return 'controlnet', False
    
    return 'unknown', False


def scan_directory(search_dir: str, min_size_mb: float = MIN_SIZE_MB) -> list:
    """扫描目录，查找模型文件"""
    results = []
    path = Path(search_dir)
    
    if not path.exists():
        return results
    
    try:
        for ext in SEARCH_EXTS:
            for file_path in path.rglob(f'*{ext}'):
                try:
                    size_mb = file_path.stat().st_size / (1024**2)
                    if size_mb >= min_size_mb:
                        size_gb = round(size_mb / 1024, 2)
                        model_type, is_confirmed = identify_model_type(str(file_path), file_path.name)
                        
                        # 如果是 unknown 且文件太大，可能是 SD 模型，跳过
                        if model_type == 'unknown' and size_gb > 1.0:
                            sd_keywords = ['v1-5', 'sdxl', 'sd15', 'vae', 'unet', 'clip']
                            is_sd = any(kw in file_path.name.lower() for kw in sd_keywords)
                            if is_sd:
                                continue
                        
                        results.append({
                            'path': str(file_path),
                            'size_gb': size_gb,
                            'size_mb': round(size_mb, 1),
                            'type': model_type,
                            'confirmed': is_confirmed,
                            'name': file_path.name,
                            'parent': file_path.parent.name,
                            'dirname': file_path.parent.parent.name if file_path.parent.parent else '',
                        })
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        pass
    
    return results


def check_cache_folders(search_dir: str) -> dict:
    """检查缓存目录中是否有完整的模型文件夹"""
    result = {}
    path = Path(search_dir)
    if not path.exists():
        return result
    
    for model_type, info in MODEL_TYPES.items():
        cache_folder = info.get('cache_folder', '')
        if cache_folder:
            folder_path = path / cache_folder
            if folder_path.exists():
                # 检查是否有 snapshot
                snapshots = list(folder_path.glob('snapshots/*'))
                if snapshots:
                    # 检查是否有模型文件
                    for snap in snapshots:
                        for f in snap.glob('*.safetensors'):
                            if f.stat().st_size > 100 * 1024 * 1024:  # >100MB
                                result[model_type] = {
                                    'exists': True,
                                    'path': str(snap),
                                    'file': f.name,
                                    'size_gb': f.stat().st_size / (1024**3),
                                }
                                break
                        if model_type in result:
                            break
                else:
                    # 可能直接就是模型目录
                    for f in folder_path.glob('*.safetensors'):
                        if f.stat().st_size > 100 * 1024 * 1024:
                            result[model_type] = {
                                'exists': True,
                                'path': str(folder_path),
                                'file': f.name,
                                'size_gb': f.stat().st_size / (1024**3),
                            }
                            break
    
    return result


def print_results(results: list, cache_results: dict, show_details: bool = False, min_size_mb: int = MIN_SIZE_MB):
    """打印搜索结果"""
    if not results:
        print("\n❌ 未找到任何模型文件")
        return
    
    # 按类型分组
    type_groups = {}
    for r in results:
        t = r['type']
        if t not in type_groups:
            type_groups[t] = []
        type_groups[t].append(r)
    
    print("\n" + "=" * 90)
    print("📊 ControlNet 模型文件搜索结果")
    print("=" * 90)
    print(f"找到 {len(results)} 个文件 (> {min_size_mb}MB)")
    print()
    
    # 统计每个类型的完整模型
    print("📋 按类型统计:")
    for t, items in sorted(type_groups.items(), key=lambda x: -len(x[1])):
        complete = [i for i in items if i['size_gb'] >= 0.5]
        print(f"   {t}: {len(items)} 个文件 ({len(complete)} 个完整)")
    print()
    
    # 🆕 显示模型状态汇总（优先显示缓存目录检查结果）
    print("🎯 ControlNet 模型状态:")
    print("-" * 90)
    print(f"{'模型':<14} {'状态':<12} {'位置'}")
    print("-" * 90)
    
    for model_type in MODEL_TYPES.keys():
        # 先检查缓存目录
        if model_type in cache_results:
            info = cache_results[model_type]
            print(f"   ✅ {model_type:<12} 完整      📂 {info['path'][:50]}...")
            continue
        
        # 再检查搜索结果
        if model_type in type_groups:
            items = type_groups[model_type]
            complete = [i for i in items if i['size_gb'] >= 0.5]
            if complete:
                print(f"   ✅ {model_type:<12} 完整      📂 {Path(complete[0]['path']).parent}")
            else:
                print(f"   ⚠️ {model_type:<12} 部分下载  ({len(items)} 个文件)")
        else:
            print(f"   ❌ {model_type:<12} 未找到")
    
    # 检查 Annotators
    if 'annotator' in type_groups:
        annotator_count = len(type_groups['annotator'])
        print(f"   📦 annotator  已安装     ({annotator_count} 个文件)")
    
    print()
    
    # 🆕 显示推荐可用模型
    available_models = []
    for model_type in ['openpose', 'lineart', 'canny', 'depth', 'hed', 'normal', 'mlsd', 'seg', 'scribble']:
        if model_type in cache_results or (model_type in type_groups and any(i['size_gb'] >= 0.5 for i in type_groups[model_type])):
            available_models.append(model_type)
    
    if available_models:
        print("💡 可直接使用的模型:")
        for m in available_models:
            print(f"   python cli.py bird_sketch -i test.jpg --controlnet {m} -n 1 --steps 10")
    
    # 显示详细路径
    if show_details:
        print("\n" + "=" * 90)
        print("📂 完整路径:")
        print("-" * 90)
        for r in results[:30]:
            print(f"  {r['path']}")


def main():
    parser = argparse.ArgumentParser(description="搜索 ControlNet 模型文件")
    parser.add_argument("--min-size", type=int, default=10, 
                        help="最小文件大小 (MB), 默认 10")
    parser.add_argument("--detail", action="store_true",
                        help="显示完整路径")
    parser.add_argument("--dirs", type=str, nargs="+",
                        help="指定搜索目录，用空格分隔")
    parser.add_argument("--json", type=str,
                        help="输出 JSON 格式到文件")
    
    args = parser.parse_args()
    
    search_dirs = args.dirs if args.dirs else SEARCH_DIRS
    
    print("=" * 90)
    print("🔍 ControlNet 模型文件搜索 v3")
    print("=" * 90)
    print(f"最小大小: {args.min_size}MB")
    print(f"搜索目录: {len(search_dirs)} 个")
    print()
    
    all_results = []
    all_cache_results = {}
    
    for search_dir in search_dirs:
        results = scan_directory(search_dir, args.min_size)
        all_results.extend(results)
        
        # 检查缓存目录
        cache_check = check_cache_folders(search_dir)
        for model_type, info in cache_check.items():
            if model_type not in all_cache_results:
                all_cache_results[model_type] = info
    
    print_results(all_results, all_cache_results, args.detail, args.min_size)
    
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已导出 JSON: {args.json}")
    
    print("\n" + "=" * 90)
    print(f"✅ 搜索完成: {len(all_results)} 个文件")


if __name__ == "__main__":
    main()