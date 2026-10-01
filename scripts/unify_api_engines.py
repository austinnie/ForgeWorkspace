# scripts/unify_api_engines.py
"""统一 API 引擎：去重留强，将所有引擎收敛到 ForgeCore 基盘"""
import shutil
from pathlib import Path

WORKSPACE = Path(r"E:\SD_OpenVINO\ForgeWorkspace")

# 1. 定义“最强版本”的来源 (ArtForge 的版本通常包含最新的高级特性)
STRONGEST_SOURCE = WORKSPACE / "apps" / "artforge" / "api_engines"

# 2. 定义目标基盘目录
TARGET_CORE_DIR = WORKSPACE / "forgecore" / "forgecore" / "engines"

# 3. 定义需要清理的 App 目录 (包含 api_engines 的地方)
APP_ENGINE_DIRS = [
    WORKSPACE / "apps" / "artforge" / "api_engines",
    WORKSPACE / "apps" / "layerforge" / "core" / "api_engines",
    WORKSPACE / "apps" / "sd_gui" / "core" / "api_engines",
    WORKSPACE / "apps" / "sd_generator" / "core" / "api_engines",
    WORKSPACE / "apps" / "promptforge" / "api_engines", # 如果存在的话
]

# 需要统一的引擎文件名 (排除 __init__.py)
ENGINE_FILES = [
    "base.py", "agnes.py", "pollinations.py", "freeapi.py", 
    "tongyi.py", "yige.py", "hunyuan.py", "huggingface.py",
    "replicate.py", "stability.py", "siliconflow.py", "openrouter.py",
    "free_multimodal_proxy.py", "freellmapi.py"
]

print("=" * 70)
print("🚀 开始统一 API 引擎 (去重留强)...")
print("=" * 70 + "\n")

# ==========================================
# 步骤 1: 将最强版本收敛到 ForgeCore
# ==========================================
print(" 步骤 1: 将最强版本收敛到 ForgeCore 基盘...")
TARGET_CORE_DIR.mkdir(parents=True, exist_ok=True)

copied_count = 0
for file_name in ENGINE_FILES:
    src_file = STRONGEST_SOURCE / file_name
    if src_file.exists():
        tgt_file = TARGET_CORE_DIR / file_name
        shutil.copy2(src_file, tgt_file)
        print(f"  ✅ 收敛: {file_name} (来源: ArtForge)")
        copied_count += 1

# 特别处理 __init__.py (使用 ArtForge 最全的导出列表)
src_init = STRONGEST_SOURCE / "__init__.py"
if src_init.exists():
    tgt_init = TARGET_CORE_DIR / "__init__.py"
    shutil.copy2(src_init, tgt_init)
    print(f"  ✅ 收敛: __init__.py (统一导出网关)")

print(f"\n 基盘收敛完毕，共 {copied_count + 1} 个文件。\n")

# ==========================================
# 步骤 2: 清理各个 App 下的重复引擎文件
# ==========================================
print("🧹 步骤 2: 清理各个 App 下的重复引擎文件...")
deleted_count = 0

for app_dir in APP_ENGINE_DIRS:
    if not app_dir.exists():
        continue
        
    print(f"\n   扫描: {app_dir.relative_to(WORKSPACE)}")
    for file_name in ENGINE_FILES:
        file_to_delete = app_dir / file_name
        if file_to_delete.exists():
            file_to_delete.unlink()
            print(f"    🗑️ 删除重复: {file_name}")
            deleted_count += 1

print(f"\n 清理完毕，共删除 {deleted_count} 个冗余文件。\n")

# ==========================================
# 步骤 3: 重写 App 的 __init__.py 为代理模式
# ==========================================
print("🔗 步骤 3: 重写 App 的 __init__.py 为 ForgeCore 代理...")

# 代理代码模板：自动将 forgecore 加入路径，并导出所有引擎
PROXY_INIT_CONTENT = '''# ==========================================
# [AUTO-GENERATED] API 引擎统一代理网关
# 本文件已清空具体实现，所有引擎统一从 ForgeCore 基盘导入
# ==========================================
import sys
from pathlib import Path

# 1. 确保 ForgeCore 根目录在 sys.path 中
_fc_root = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(_fc_root) not in sys.path:
    sys.path.insert(0, str(_fc_root))

# 2. 统一从 ForgeCore 导入所有 API 引擎
try:
    from forgecore.engines import *
    from forgecore.engines import create_engine, create_api_engine
    from forgecore.engines import (
        BaseEngine, TongyiEngine, YigeEngine, HunyuanEngine, 
        HuggingFaceEngine, PollinationsEngine, AgnesEngine, 
        FreeAPIEngine, ReplicateEngine, StabilityEngine,
        SiliconFlowEngine, OpenRouterEngine, FreeMultimodalProxyEngine, FreeLLMAPIEngine
    )
except ImportError as e:
    print(f"️ 从 ForgeCore 导入 API 引擎失败: {e}")
    print(" 请检查 forgecore/forgecore/engines/ 目录是否完整。")
'''

replaced_count = 0
for app_dir in APP_ENGINE_DIRS:
    if not app_dir.exists():
        continue
        
    init_file = app_dir / "__init__.py"
    # 即使 __init__.py 不存在也创建一个
    init_file.write_text(PROXY_INIT_CONTENT, encoding="utf-8")
    print(f"  ✅ 重写代理: {init_file.relative_to(WORKSPACE)}")
    replaced_count += 1

print(f"\n🎉 代理重写完毕，共 {replaced_count} 个目录。\n")

# ==========================================
# 总结
# ==========================================
print("=" * 70)
print("🏆 API 引擎统一与去重任务完成！")
print("=" * 70)
print("💡 架构现状:")
print("   - 唯一真实代码位置: forgecore/forgecore/engines/")
print("   - 各 App 调用方式: from api_engines import create_engine (保持不变)")
print("   - 未来维护: 只需修改 ForgeCore 中的引擎，所有 App 自动生效！")
print("=" * 70)