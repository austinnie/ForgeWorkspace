# forgecore/forgecore/pipeline/registry.py
"""Pipeline 注册表 - 兼容旧代码的 Step 注册机制"""
from typing import Dict, Type, List
from .base import BaseStep

class PipelineRegistry:
    """全局 Step 注册表"""
    _registry: Dict[str, Type[BaseStep]] = {}
    
    @classmethod
    def register_step(cls, name: str, step_class: Type[BaseStep]):
        """注册一个 Step"""
        if not issubclass(step_class, BaseStep):
            # 兼容旧代码：如果旧 Step 没有继承 BaseStep，动态修改其基类
            step_class.__bases__ = (BaseStep,)
        cls._registry[name] = step_class
        
    @classmethod
    def get_step(cls, name: str) -> Type[BaseStep]:
        """获取已注册的 Step"""
        if name not in cls._registry:
            raise ValueError(f"❌ 未注册的 Step: {name}。可用: {list(cls._registry.keys())}")
        return cls._registry[name]
        
    @classmethod
    def list_steps(cls) -> List[str]:
        """列出所有可用的 Step"""
        return sorted(cls._registry.keys())

# 兼容旧代码的快捷方式
register_step = PipelineRegistry.register_step