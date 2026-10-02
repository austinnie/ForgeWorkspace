# forgecore/config/paths.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 自动定位项目根目录 (当前文件在 forgecore/config/paths.py，往上推 2 级是 ForgeWorkspace)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 2. 加载环境变量
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Paths:
    """全局绝对路径注册表 - 所有路径均为 pathlib.Path 绝对路径对象"""
    
    # 核心模型基目录 (直接指定绝对路径，绝不使用相对路径)
    BASE_MODELS_DIR = Path(os.getenv("BASE_MODELS_DIR", r"E:\SD_OpenVINO\models"))
    
    # --- 外部模型目录 (直接指定，无相对路径) ---
    SD15_DIR = BASE_MODELS_DIR / "sd-v1-5"
    SDXL_DIR = BASE_MODELS_DIR / "sdxl"
    SD15_LORA_DIR = BASE_MODELS_DIR / "sd15-lora"
    SDXL_LORA_DIR = BASE_MODELS_DIR / "sdxl-lora"
    CONTROLNET_DIR = BASE_MODELS_DIR / "controlnet"
    
    # --- 项目内部目录 (基于 PROJECT_ROOT 的绝对路径) ---
    OUTPUT_DIR = PROJECT_ROOT / "output"
    CACHE_DIR = PROJECT_ROOT / "cache"
    CONFIG_DIR = PROJECT_ROOT / "data" / "configs"
    
    # --- 关键配置文件路径 ---
    USER_CONFIG_FILE = CONFIG_DIR / "user_config.json"
    LORA_INDEX_FILE = CONFIG_DIR / "lora_index.json"

    @classmethod
    def ensure_dirs(cls):
        """确保所有必要的目录存在"""
        for dir_path in [cls.OUTPUT_DIR, cls.CACHE_DIR, cls.CONFIG_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    @classmethod
    def get_all_paths_as_dict(cls) -> dict:
        """供调试或前端展示使用，返回字符串格式的绝对路径"""
        return {k: str(v.resolve()) for k, v in cls.__dict__.items() if isinstance(v, Path)}