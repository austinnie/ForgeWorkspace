# scripts/fix_forgecore.py
"""修复 ForgeCore 内部导入路径和接口统一"""
from pathlib import Path

CORE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore")

# ============================================================
# 修复 1: forgecore/__init__.py - 添加 .env 自动加载
# ============================================================
init_py = CORE / "__init__.py"
init_py.write_text('''"""ForgeCore - AI 创作通用基础库"""
__version__ = "1.0.0"

import os
from pathlib import Path

# 🔥 自动加载 ForgeWorkspace 根目录的 .env
def _load_env():
    """向上查找 .env 文件（兼容多种运行方式）"""
    try:
        from dotenv import load_dotenv
        # 从当前文件向上找: forgecore -> forgecore -> ForgeWorkspace
        search = Path(__file__).resolve().parent
        for _ in range(5):
            env_file = search / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                return str(env_file)
            search = search.parent
        # 兜底：从系统环境变量加载
        load_dotenv()
        return "(system env)"
    except ImportError:
        return "(dotenv not installed)"

_env_source = _load_env()
''', encoding="utf-8")
print(f"✅ 修复 1: {init_py.relative_to(CORE.parent)}")

# ============================================================
# 修复 2: engines/__init__.py - 统一函数名 + 自动从 .env 读取 Key
# ============================================================
engines_init = CORE / "engines" / "__init__.py"

# 先读取旧内容，保留引擎导入
old_content = engines_init.read_text(encoding="utf-8")

# 提取所有 from .xxx import XxxEngine 行
import_lines = []
for line in old_content.splitlines():
    stripped = line.strip()
    if stripped.startswith("from .") and "import" in stripped and "Engine" in stripped:
        import_lines.append(stripped)

# 如果没有找到导入行，使用默认列表
if not import_lines:
    import_lines = [
        "from .base import BaseEngine",
        "from .tongyi import TongyiEngine",
        "from .yige import YigeEngine",
        "from .hunyuan import HunyuanEngine",
        "from .huggingface import HuggingFaceEngine",
        "from .pollinations import PollinationsEngine",
        "from .agnes import AgnesEngine",
        "from .freeapi import FreeAPIEngine",
    ]

engines_init.write_text(f'''# forgecore/engines/__init__.py
"""API 图像生成引擎 - 统一网关"""
import os

# 引擎导入
{chr(10).join(import_lines)}

# 🔥 引擎注册表
_ENGINE_MAP = {{}}
for _name, _obj in list(globals().items()):
    if _name.endswith("Engine") and _name != "BaseEngine" and isinstance(_obj, type):
        # 例如 TongyiEngine -> "tongyi"
        _key = _name.replace("Engine", "").lower()
        _ENGINE_MAP[_key] = _obj

def create_engine(provider: str, config: dict = None) -> "BaseEngine":
    """
    统一引擎创建接口（兼容 ArtForge / PromptForge / LayerForge 调用方式）
    
    用法:
        engine = create_engine("pollinations")          # 免费，无需 Key
        engine = create_engine("agnes")                 # 自动从 .env 读取 Key
        engine = create_engine("tongyi", {{"TONGYI_API_KEY": "xxx"}})  # 手动传 Key
    """
    if config is None:
        config = {{}}
    
    provider = provider.lower().strip()
    
    # 自动从环境变量补充缺失的 Key
    env_keys = [
        "AGNES_API_KEY", "AGNES_BASE_URL", "AGNES_IMAGE_MODEL",
        "AGNES_VIDEO_MODEL", "AGNES_VISION_MODEL", "AGNES_TEXT_MODEL",
        "TONGYI_API_KEY", "TONGYI_MODEL",
        "YIGE_API_KEY", "YIGE_SECRET_KEY",
        "HUNYUAN_SECRET_ID", "HUNYUAN_SECRET_KEY",
        "HF_API_TOKEN", "HF_MODEL",
        "POLLINATIONS_MODEL",
        "FREEAPI_MODEL",
    ]
    for key in env_keys:
        if key not in config:
            val = os.getenv(key)
            if val:
                config[key] = val
    
    # 查找引擎类
    engine_cls = _ENGINE_MAP.get(provider)
    if engine_cls is None:
        available = ", ".join(sorted(_ENGINE_MAP.keys()))
        raise ValueError(f"❌ 未知引擎: {{provider}}\\n   可用引擎: {{available}}")
    
    return engine_cls(config=config)

# 🔥 兼容 LayerForge 旧接口
create_api_engine = create_engine

__all__ = ["BaseEngine", "create_engine", "create_api_engine"]
''', encoding="utf-8")
print(f"✅ 修复 2: {engines_init.relative_to(CORE.parent)}")

# ============================================================
# 修复 3: prompt/__init__.py - 统一导出
# ============================================================
prompt_init = CORE / "prompt" / "__init__.py"
prompt_init.write_text('''# forgecore/prompt/__init__.py
"""提示词工坊 - 统一导出"""

# 尝试导入 ArtForge 的 PromptBuilder
try:
    from .builder import PromptBuilder
except ImportError:
    PromptBuilder = None

# 尝试导入 LayerForge 的 PromptComposer
try:
    from .composer import PromptComposer
except ImportError:
    PromptComposer = None

__all__ = ["PromptBuilder", "PromptComposer"]
''', encoding="utf-8")
print(f"✅ 修复 3: {prompt_init.relative_to(CORE.parent)}")

# ============================================================
# 修复 4: 检查引擎基类是否接受 config 参数
# ============================================================
base_py = CORE / "engines" / "base.py"
if base_py.exists():
    content = base_py.read_text(encoding="utf-8")
    # 检查 __init__ 是否接受 config 参数
    if "def __init__(self" in content and "config" not in content.split("def __init__")[1].split("def ")[0][:200]:
        print(f"⚠️ 注意: {base_py.name} 的 __init__ 可能不接受 config 参数")
        print(f"   旧代码可能使用 create_api_engine(provider, config) 方式传参")
        print(f"   如果测试报错，需要手动修改 base.py 的构造函数")
    else:
        print(f"✅ 修复 4: base.py 构造函数检查通过")
else:
    print(f"⚠️ 未找到 base.py")

print("\n🎉 ForgeCore 修复完成！")
print("👉 下一步: 运行 python apps/artforge/main.py 验证调用")