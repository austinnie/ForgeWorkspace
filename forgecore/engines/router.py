# forgecore/forgecore/engines/router.py
import os
from .local_engine import OpenVINOEngine

# 假设你原有的 API 引擎工厂函数在这里或已被导入
# from .api_engines import create_api_engine 

def get_engine(
    engine_type: str = "auto", 
    model_type: str = "sd15", 
    device: str = "CPU",
    **api_kwargs
):
    """
    统一引擎工厂：根据配置自动路由到 API 引擎或本地引擎。
    
    :param engine_type: "api", "local", "auto"
    :param model_type: "sd15", "sdxl" 等
    """
    # 读取全局开关 (在 .env 中配置 USE_LOCAL_MODEL=true)
    use_local_env = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

    # 路由逻辑
    if engine_type == "local" or (engine_type == "auto" and use_local_env):
        # 返回本地引擎
        return OpenVINOEngine(model_type=model_type, device=device)
    
    else:
        # 返回 API 引擎 (这里调用你原有的 API 引擎创建逻辑)
        # return create_api_engine(engine_type, **api_kwargs)
        raise NotImplementedError("请在此处接入你原有的 API 引擎创建逻辑")