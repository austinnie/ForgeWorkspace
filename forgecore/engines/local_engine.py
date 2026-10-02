# forgecore/engines/local_engine.py
import os
import time
from pathlib import Path
from abc import ABC, abstractmethod
from forgecore.config.paths import Paths
from forgecore.config.settings import settings

class BaseLocalEngine(ABC):
    """本地模型推理引擎基类"""
    
    def __init__(self, model_type: str = "sd15", device: str = "CPU"):
        self.model_type = model_type
        self.device = device
        self.pipeline = None  # 这里改为 pipeline，符合 diffusers 习惯
        self.model_path: Path = None

    def load_model(self, model_path: str = None) -> "BaseLocalEngine":
        """加载本地模型"""
        start_time = time.time()
        
        # 1. 获取绝对路径
        if not model_path:
            model_path = settings.get_default_model_path(self.model_type)
        
        self.model_path = Path(model_path).resolve()
        
        # 2. 校验路径
        if not self.model_path.exists():
            raise FileNotFoundError(f"本地模型文件不存在: {self.model_path}")
        
        print(f"\n{'='*60}")
        print(f"🚀 开始加载本地模型: {self.model_path.name}")
        print(f"📏 文件大小: {self.model_path.stat().st_size / (1024**2):.2f} MB")
        print(f"💻 目标设备: {self.device}")
        print(f"{'='*60}")

        # 3. 执行具体的加载逻辑 (子类实现)
        self._do_load(self.model_path)
        
        elapsed = time.time() - start_time
        print(f"✅ 模型加载完成！耗时: {elapsed:.2f} 秒")
        print(f"{'='*60}\n")
        return self

    @abstractmethod
    def _do_load(self, absolute_path: Path):
        """子类实现具体的模型加载逻辑"""
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        """子类实现具体的推理逻辑"""
        pass


class DiffusersEngine(BaseLocalEngine):
    """
    基于 HuggingFace Diffusers 的本地推理引擎 (CPU/GPU 通用)
    这是最稳妥的加载方式
    """
    
    def _do_load(self, absolute_path: Path):
        print("   [1/3] 正在导入 diffusers 库...")
        from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
        import torch
        
        # 判断是 SD1.5 还是 SDXL
        is_sdxl = "sdxl" in str(absolute_path).lower() or "xl" in str(absolute_path).lower()
        
        print(f"   [2/3] 正在读取模型权重 (这步最慢，请耐心等待 30-60 秒)...")
        # CPU 模式下必须使用 float32，否则会报错或极慢
        dtype = torch.float32 if self.device == "CPU" else torch.float16
        
        if is_sdxl:
            self.pipeline = StableDiffusionXLPipeline.from_single_file(
                str(absolute_path),
                torch_dtype=dtype,
                use_safetensors=True,
                low_cpu_mem_usage=True
            )
        else:
            self.pipeline = StableDiffusionPipeline.from_single_file(
                str(absolute_path),
                torch_dtype=dtype,
                safety_checker=None,
                requires_safety_checker=False,
                use_safetensors=True,
                low_cpu_mem_usage=True
            )
            
        print(f"   [3/3] 正在应用内存优化 (VAE Slicing & Attention Slicing)...")
        # 开启内存优化，防止 CPU 内存爆掉
        if hasattr(self.pipeline, 'enable_vae_slicing'):
            self.pipeline.enable_vae_slicing()
        if hasattr(self.pipeline, 'enable_attention_slicing'):
            self.pipeline.enable_attention_slicing()
            
        print(f"   -> 管道初始化完成，准备就绪。")

    def generate(self, prompt: str, negative_prompt: str = "", width: int = 512, height: int = 512, 
                 num_inference_steps: int = 25, guidance_scale: float = 7.5, seed: int = None) -> Image.Image:
        """执行真实的本地推理"""
        if self.pipeline is None:
            raise RuntimeError("模型未加载，请先调用 load_model()")
        
        print(f"🎨 开始推理: {prompt[:50]}...")
        print(f"⚙️ 参数: steps={num_inference_steps}, cfg={guidance_scale}, seed={seed}")
        
        import torch
        from PIL import Image
        
        # 设置随机种子
        if seed is None or seed == -1:
            seed = torch.randint(0, 2**32 - 1, (1,)).item()
        generator = torch.Generator("cpu").manual_seed(seed)
        
        # 执行推理
        print("🔄 正在生成图片...")
        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        )
        
        # 提取图片
        image = result.images[0]
        print(f"✅ 推理完成，图片尺寸: {image.size}")
        
        return image

class OpenVINOEngine(BaseLocalEngine):
    """
    基于 OpenVINO 的本地推理引擎 (Intel CPU/GPU 加速)
    如果你安装了 optimum-intel，可以使用这个，速度比上面快 3-5 倍
    """
    def _do_load(self, absolute_path: Path):
        print("   [1/2] 正在导入 OpenVINO (optimum-intel)...")
        try:
            from optimum.intel import OVStableDiffusionPipeline
        except ImportError:
            print("    未安装 optimum-intel，请运行: pip install optimum[openvino]")
            print("   ⚠️ 自动降级使用普通 Diffusers 引擎...")
            # 降级逻辑
            DiffusersEngine._do_load(self, absolute_path)
            return

        print(f"   [2/2] 正在编译 OpenVINO 模型 (首次加载可能需要 1-2 分钟)...")
        self.pipeline = OVStableDiffusionPipeline.from_single_file(
            str(absolute_path),
            export=True, # 自动将 safetensors 转换为 OpenVINO IR 格式
            compile=True
        )
        print(f"   -> OpenVINO 编译完成。")

    def generate(self, prompt: str, **kwargs):
        if self.pipeline is None:
            raise RuntimeError("模型未加载")
        print(f"🚀 OpenVINO 推理中: {prompt[:50]}...")
        return None


# 默认导出 DiffusersEngine，保证一定能跑
LocalEngine = DiffusersEngine