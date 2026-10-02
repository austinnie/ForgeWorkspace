# forgecore/forgecore/engines/local_engine.py
import os
from pathlib import Path
from abc import ABC, abstractmethod
from forgecore.config.paths import Paths
from forgecore.config.settings import settings

class BaseLocalEngine(ABC):
    """本地模型推理引擎基类"""
    
    def __init__(self, model_type: str = "sd15", device: str = "CPU"):
        self.model_type = model_type
        self.device = device
        self.model = None
        self.model_path: Path = None

    def load_model(self, model_path: str = None) -> "BaseLocalEngine":
        """
        加载本地模型。
        如果不传 model_path，则自动从 settings 获取用户配置的默认模型绝对路径。
        """
        # 1. 获取绝对路径
        if not model_path:
            model_path = settings.get_default_model_path(self.model_type)
        
        self.model_path = Path(model_path).resolve()
        
        # 2. 校验路径
        if not self.model_path.exists():
            raise FileNotFoundError(f"本地模型文件不存在: {self.model_path}")
        if not self.model_path.is_absolute():
            raise ValueError(f"模型路径必须是绝对路径: {self.model_path}")

        # 3. 执行具体的加载逻辑 (子类实现)
        print(f"🚀 正在加载本地模型: {self.model_path.name} (设备: {self.device})")
        self._do_load(self.model_path)
        return self

    @abstractmethod
    def _do_load(self, absolute_path: Path):
        """子类实现具体的模型加载逻辑 (如 OpenVINO, PyTorch, ONNX)"""
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        """子类实现具体的推理逻辑"""
        pass


class OpenVINOEngine(BaseLocalEngine):
    """OpenVINO 本地推理引擎实现 (示例)"""
    
    def _do_load(self, absolute_path: Path):
        # 这里替换为你真实的 OpenVINO 加载代码
        # import openvino as ov
        # core = ov.Core()
        # self.model = core.read_model(model=str(absolute_path))
        # self.compiled_model = core.compile_model(self.model, self.device)
        pass

    def generate(self, prompt: str, **kwargs):
        if not self.model:
            raise RuntimeError("模型未加载，请先调用 load_model()")
        # 这里替换为你真实的 OpenVINO 推理代码
        print(f"🎨 使用 OpenVINO 本地生成: {prompt[:50]}...")
        return None # 返回生成的图像或结果