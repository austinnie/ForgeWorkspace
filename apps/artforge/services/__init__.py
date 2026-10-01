# ==========================================
# [AUTO-GENERATED] API 引擎统一代理网关
# 本文件已清空具体实现，所有后处理服务统一从 ForgeCore 基盘导入
# ==========================================
import sys
from pathlib import Path

# 1. 确保 ForgeCore 根目录在 sys.path 中
_fc_root = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(_fc_root) not in sys.path:
    sys.path.insert(0, str(_fc_root))

# 2. 统一从 ForgeCore 导入所有后处理服务
try:
    from forgecore.post_process import *
    from forgecore.post_process import (
        AgingProcessor, InscriptionGenerator, SealGenerator, WatermarkProcessor
    )
except ImportError as e:
    print(f"⚠️ 从 ForgeCore 导入后处理服务失败: {e}")
    print("  请检查 forgecore/forgecore/post_process/ 目录是否完整。")
