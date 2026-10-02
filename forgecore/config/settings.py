# forgecore/forgecore/config/settings.py
import json
from pathlib import Path
from .paths import Paths
from .registry import ModelRegistry

class Settings:
    """单例配置管理器 (替代原有的 app_config.py)"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        Paths.ensure_dirs()
        self.user_config = {}
        if Paths.USER_CONFIG_FILE.exists():
            try:
                with open(Paths.USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.user_config = json.load(f)
            except Exception:
                self.user_config = {}

    def get_default_model_path(self, model_type: str = "sd15") -> str:
        """获取用户上次保存的默认模型绝对路径"""
        key = f"default_{model_type}_model"
        path_str = self.user_config.get(key)
        if path_str and Path(path_str).exists():
            return str(Path(path_str).resolve())
        
        # 兜底：返回该类型目录下的第一个模型
        checkpoints = ModelRegistry.scan_checkpoints(model_type)
        if checkpoints:
            return checkpoints[0]["absolute_path"]
        return ""

    def save_default_model(self, model_type: str, absolute_path: str):
        """保存默认模型 (强制要求传入绝对路径)"""
        path_obj = Path(absolute_path).resolve()
        if not path_obj.exists():
            raise ValueError(f"模型路径不存在: {absolute_path}")
        self.user_config[f"default_{model_type}_model"] = str(path_obj)
        self._save()

    def _save(self):
        with open(Paths.USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.user_config, f, ensure_ascii=False, indent=2)

# 全局单例实例，其他模块直接 import settings 使用
settings = Settings()