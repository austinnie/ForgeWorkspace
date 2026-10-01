# forgecore/pipeline/base.py
"""Pipeline 基础定义 - 彻底解耦 GUI 的纯数据/逻辑层"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List
from PIL import Image
from enum import Enum
import time

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StepContext:
    """步骤执行上下文 - 在流水线中传递状态"""
    input_image: Optional[Image.Image] = None
    input_path: Optional[str] = None
    output_dir: str = "./output"
    global_config: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    
    # 🔥 核心：取消机制 (由外部 Runner 注入，替代旧代码的 Tkinter cancel_flag)
    _cancel_flag: Callable[[], bool] = field(default=lambda: False, repr=False)
    
    def is_cancelled(self) -> bool:
        return self._cancel_flag()

@dataclass
class StepResult:
    """步骤执行结果"""
    status: StepStatus
    output_image: Optional[Image.Image] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.status == StepStatus.SUCCESS

class BaseStep:
    """所有处理步骤的基类 (如: WatercolorStep, CyberpunkStep)"""
    name: str = "BaseStep"
    
    def execute(self, context: StepContext, progress_cb: Callable[[float, str], None]) -> StepResult:
        """
        执行步骤
        :param context: 上下文 (包含输入图片、配置等)
        :param progress_cb: 进度回调 (替代旧代码的 self.app.update_progress)
        """
        raise NotImplementedError("子类必须实现 execute 方法")
        
    def __repr__(self):
        return f"<{self.__class__.__name__}>"
