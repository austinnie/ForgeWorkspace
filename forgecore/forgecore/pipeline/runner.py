# forgecore/pipeline/runner.py
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
