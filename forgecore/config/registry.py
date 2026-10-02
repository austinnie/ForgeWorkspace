# forgecore/forgecore/config/registry.py
from pathlib import Path
from .paths import Paths

class ModelRegistry:
    """统一的模型与 LoRA 资源注册表 (替代原有的 lora_index.py 和散落的扫描逻辑)"""

    @staticmethod
    def scan_loras(model_type: str = "sd15") -> list:
        """扫描指定类型的 LoRA，返回包含绝对路径的标准字典列表"""
        target_dir = Paths.SD15_LORA_DIR if model_type == "sd15" else Paths.SDXL_LORA_DIR
        
        if not target_dir.exists():
            return []
        
        loras = []
        for ext in ["*.safetensors", "*.ckpt"]:
            for file in target_dir.glob(ext):
                loras.append({
                    "name": file.stem,
                    "filename": file.name,
                    "absolute_path": str(file.resolve()),  # 强制绝对路径
                    "size_mb": round(file.stat().st_size / (1024**2), 2),
                    "type": model_type
                })
        return sorted(loras, key=lambda x: x["name"])

    @staticmethod
    def scan_checkpoints(model_type: str = "sd15") -> list:
        """扫描主模型 (Checkpoints)"""
        target_dir = Paths.SD15_DIR if model_type == "sd15" else Paths.SDXL_DIR
        if not target_dir.exists():
            return []
            
        checkpoints = []
        for file in target_dir.glob("*.safetensors"):
            checkpoints.append({
                "name": file.stem,
                "absolute_path": str(file.resolve()),
                "size_mb": round(file.stat().st_size / (1024**2), 2),
                "type": model_type
            })
        return sorted(checkpoints, key=lambda x: x["name"])