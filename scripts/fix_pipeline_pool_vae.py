# scripts/fix_pipeline_pool_vae.py
"""修复 pipeline_pool.py 中的 VAE slicing/tiling 兼容性问题"""
import re
from pathlib import Path

POOL_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\sd_gui\utils\pipeline_pool.py")

if not POOL_FILE.exists():
    print("❌ 找不到 pipeline_pool.py")
    exit(1)

content = POOL_FILE.read_text(encoding="utf-8")

# 1. 修复 enable_vae_slicing
content = re.sub(
    r"(\s+)pipe\.enable_vae_slicing\(\)",
    r"\1if hasattr(pipe, 'enable_vae_slicing'):\n\1    pipe.enable_vae_slicing()",
    content
)

# 2. 修复 enable_vae_tiling
content = re.sub(
    r"(\s+)pipe\.enable_vae_tiling\(\)",
    r"\1if hasattr(pipe, 'enable_vae_tiling'):\n\1    pipe.enable_vae_tiling()",
    content
)

# 3. 修复 enable_model_cpu_offload (如果存在)
content = re.sub(
    r"(\s+)pipe\.enable_model_cpu_offload\(\)",
    r"\1if hasattr(pipe, 'enable_model_cpu_offload'):\n\1    pipe.enable_model_cpu_offload()",
    content
)

# 4. 修复 enable_sequential_cpu_offload (如果存在)
content = re.sub(
    r"(\s+)pipe\.enable_sequential_cpu_offload\(\)",
    r"\1if hasattr(pipe, 'enable_sequential_cpu_offload'):\n\1    pipe.enable_sequential_cpu_offload()",
    content
)

POOL_FILE.write_text(content, encoding="utf-8")
print("✅ 已修复 pipeline_pool.py 中的 VAE 显存优化方法调用 (添加 hasattr 安全检查)")
print("\n👉 请关闭当前运行的 GUI，然后重新运行: python apps/sd_gui/main.py")