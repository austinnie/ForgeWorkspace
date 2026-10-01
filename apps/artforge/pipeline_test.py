# apps/artforge/pipeline_test.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 ForgeCore Pipeline 引擎 (模拟风格转换链)"""
import sys
import time
from pathlib import Path
from PIL import Image, ImageFilter

# 1. 注入 ForgeCore
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

from forgecore.pipeline import BaseStep, StepContext, StepResult, StepStatus, PipelineRunner

# ============================================================
# 模拟 Step 1: 水彩风格化 (替代真实的 Diffusers 图生图)
# ============================================================
class WatercolorStep(BaseStep):
    name = "水彩风格化"
    
    def execute(self, context: StepContext, progress_cb) -> StepResult:
        print("   🎨 正在模拟加载 ControlNet (Canny)...")
        progress_cb(0.2, "加载模型中...")
        time.sleep(1) # 模拟加载模型
        
        if context.is_cancelled(): return StepResult(status=StepStatus.SKIPPED)
        
        print("   🖌️ 正在应用水彩滤镜...")
        progress_cb(0.8, "生成中...")
        time.sleep(1) # 模拟生图
        
        # 用 Pillow 模拟效果
        img = context.input_image.copy()
        img = img.filter(ImageFilter.SMOOTH)
        img = img.filter(ImageFilter.CONTOUR)
        
        return StepResult(
            status=StepStatus.SUCCESS,
            output_image=img,
            metadata={"style": "watercolor", "mock": True}
        )

# ============================================================
# 模拟 Step 2: EXIF 相机注入 (复用我们搬过来的 forgecore.image)
# ============================================================
class ExifInjectStep(BaseStep):
    name = "EXIF相机注入"
    
    def execute(self, context: StepContext, progress_cb) -> StepResult:
        progress_cb(0.5, "注入元数据...")
        print("   📷 正在注入富士相机 EXIF 数据...")
        time.sleep(0.5)
        
        # 这里可以调用真实的 forgecore.image.exif_injector
        return StepResult(
            status=StepStatus.SUCCESS,
            output_image=context.input_image, # 透传图片
            metadata={"camera": "FUJIFILM X-T4"}
        )

# ============================================================
# 主测试流程
# ============================================================
def main():
    print("=" * 60)
    print("🚀 ForgeCore Pipeline 引擎测试")
    print("=" * 60)
    
    # 1. 准备一张测试图 (用之前生成的天狗，或者新建一张)
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 找一张现有的图，或者创建一张纯色图
    test_img_path = output_dir / "test_input.png"
    if not test_img_path.exists():
        print("⚠️ 未找到测试图，正在生成一张纯色图...")
        img = Image.new('RGB', (512, 512), color=(100, 150, 200))
        img.save(test_img_path)
        
    input_img = Image.open(test_img_path)
    
    # 2. 构建 Context
    context = StepContext(
        input_image=input_img,
        input_path=str(test_img_path),
        output_dir=str(output_dir),
        global_config={"strength": 0.6, "cfg": 7.5} # 模拟参数
    )
    
    # 3. 组装 Pipeline (就像搭积木一样)
    pipeline = PipelineRunner([
        WatercolorStep(),
        ExifInjectStep(),
    ])
    
    # 4. 定义进度回调 (这里可以对接 Tkinter/Gradio，或者只打印)
    def my_progress_cb(value, msg):
        bar_len = 30
        filled = int(bar_len * value)
        bar = '█' * filled + '-' * (bar_len - filled)
        print(f"\r   [{bar}] {value*100:.0f}% | {msg}", end="", flush=True)
        if value >= 1.0: print() # 换行
        
    # 5. 运行！
    print("\n🏃 开始运行流水线...")
    start = time.time()
    results = pipeline.run(context, progress_cb=my_progress_cb)
    elapsed = time.time() - start
    
    # 6. 检查结果
    print("\n" + "=" * 60)
    print("📊 流水线执行报告:")
    for i, res in enumerate(results):
        step_name = pipeline.steps[i].name
        status_icon = "✅" if res.success else "❌"
        print(f"  {status_icon} {step_name}: {res.status.value} | 元数据: {res.metadata}")
        
    # 保存最终结果
    final_img = context.input_image
    final_path = output_dir / "pipeline_final_output.png"
    final_img.save(final_path)
    
    print(f"\n🎉 测试完成！总耗时: {elapsed:.2f}s")
    print(f"📁 最终图片已保存: {final_path.resolve()}")
    
    import os
    os.startfile(final_path.resolve())

if __name__ == "__main__":
    main()