# scripts/setup_pipeline.py
"""初始化 ForgeCore Pipeline 引擎骨架"""
from pathlib import Path

PIPELINE_DIR = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline")
PIPELINE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. base.py - 定义 Step、Context、Result (彻底解耦 GUI)
# ============================================================
(PIPELINE_DIR / "base.py").write_text('''# forgecore/pipeline/base.py
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
''', encoding="utf-8")

# ============================================================
# 2. runner.py - 流水线运行器 (支持批量、取消、进度)
# ============================================================
(PIPELINE_DIR / "runner.py").write_text('''# forgecore/pipeline/runner.py
"""Pipeline 运行器 - 负责按顺序执行 Steps"""
import time
import logging
from typing import List, Callable, Optional
from .base import BaseStep, StepContext, StepResult, StepStatus

logger = logging.getLogger("forgecore.pipeline")

class PipelineRunner:
    """流水线运行器"""
    
    def __init__(self, steps: List[BaseStep]):
        self.steps = steps
        self._is_cancelled = False
        
    def cancel(self):
        """外部调用以取消运行"""
        self._is_cancelled = True
        logger.info("⏹️ 收到取消信号")
        
    def run(self, context: StepContext, progress_cb: Optional[Callable[[float, str], None]] = None) -> List[StepResult]:
        """
        运行整个流水线
        :return: 每个 Step 的结果列表
        """
        results = []
        total_steps = len(self.steps)
        
        # 注入取消标志到 Context
        context._cancel_flag = lambda: self._is_cancelled
        
        for idx, step in enumerate(self.steps):
            if self._is_cancelled:
                logger.info(f"⏹️ 流水线已取消，跳过后续 {total_steps - idx} 个步骤")
                break
                
            step_name = step.name or step.__class__.__name__
            logger.info(f"🚀 [{idx+1}/{total_steps}] 开始执行: {step_name}")
            
            if progress_cb:
                progress_cb(idx / total_steps, f"正在执行: {step_name}...")
                
            start_time = time.time()
            try:
                # 执行具体步骤
                result = step.execute(context, progress_cb)
                elapsed = time.time() - start_time
                
                # 将结果存入 Context，供后续 Step 使用
                context.step_results[step_name] = result
                
                # 如果步骤输出了新图片，更新 Context 的 input_image (链式处理)
                if result.success and result.output_image:
                    context.input_image = result.output_image
                    
                logger.info(f"✅ [{idx+1}/{total_steps}] {step_name} 完成 (耗时 {elapsed:.2f}s)")
                results.append(result)
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ [{idx+1}/{total_steps}] {step_name} 失败: {e}")
                results.append(StepResult(
                    status=StepStatus.FAILED, 
                    error=str(e),
                    metadata={"elapsed": elapsed}
                ))
                # 根据策略：可以选择中断或继续
                # 这里选择记录错误并继续下一个
                
        if progress_cb:
            progress_cb(1.0, "✅ 流水线执行完毕")
            
        return results
''', encoding="utf-8")

# ============================================================
# 3. __init__.py - 统一导出
# ============================================================
(PIPELINE_DIR / "__init__.py").write_text('''# forgecore/pipeline/__init__.py
from .base import BaseStep, StepContext, StepResult, StepStatus
from .runner import PipelineRunner

__all__ = ["BaseStep", "StepContext", "StepResult", "StepStatus", "PipelineRunner"]
''', encoding="utf-8")

print("✅ ForgeCore Pipeline 引擎骨架已生成！")
print("👉 下一步: 运行 python apps/artforge/pipeline_test.py 验证流水线")