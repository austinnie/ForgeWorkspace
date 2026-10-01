# ==========================================
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
