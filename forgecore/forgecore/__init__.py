"""ForgeCore - AI 创作通用基础库"""
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
