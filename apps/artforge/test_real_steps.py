# apps/artforge/test_real_steps.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 ForgeCore 真实风格 Step (使用之前生成的天狗图片)"""
import sys
import time
from pathlib import Path
from PIL import Image

# 1. 注入 ForgeCore
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

from forgecore.pipeline import PipelineRunner, StepContext, PipelineRegistry

# 🔥 2. 触发 steps 目录的自动导入与注册
import forgecore.pipeline.steps 

def main():
    print("=" * 60)
    print("🎨 ForgeCore 真实风格 Step 测试")
    print("=" * 60)
    
    # 3. 查看成功注册了多少个 Step
    available_steps = PipelineRegistry.list_steps()
    print(f"\n✅ 成功加载 {len(available_steps)} 种风格 Step！")
    print(f"📋 前 10 个预览: {available_steps[:10]}...\n")
    
    # 4. 准备输入图片 (使用之前生成的天狗，或者随便找一张图)
    output_dir = Path(__file__).parent / "output"
    input_img_path = output_dir / "tengu_ukiyo_e_1790845159.png" # 替换为您实际的文件名
    
    if not input_img_path.exists():
        # 如果没有，就用 pipeline_test 生成的纯色图代替
        input_img_path = output_dir / "pipeline_final_output.png"
        if not input_img_path.exists():
            print("⚠️ 未找到测试图，正在生成一张...")
            img = Image.new('RGB', (512, 512), color=(100, 150, 200))
            img.save(input_img_path)
            
    input_img = Image.open(input_img_path).convert("RGB")
    
    # 5. 挑选 3 个真实的 Step 进行链式处理
    # (注意：具体的 Step 名称取决于您旧代码里的注册名，这里用常见的名称举例)
    target_styles = ["watercolor", "cyberpunk", "dunhuang_fresco"] 
    # 如果旧代码里叫别的名字（比如 "samurai", "ceramic"），请自行替换
    
    steps_to_run = []
    for style in target_styles:
        try:
            step_cls = PipelineRegistry.get_step(style)
            steps_to_run.append(step_cls())
            print(f"  🎯 选中风格: {style} ({step_cls.__name__})")
        except ValueError:
            print(f"  ⚠️ 跳过未找到的风格: {style}")
            
    if not steps_to_run:
        print("❌ 没有可用的 Step，请检查 steps 目录或注册名。")
        return

    # 6. 构建 Context 并运行
    context = StepContext(
        input_image=input_img,
        input_path=str(input_img_path),
        output_dir=str(output_dir),
        global_config={"strength": 0.6, "cfg": 7.5, "device": "cpu"} # 根据旧代码参数调整
    )
    
    pipeline = PipelineRunner(steps_to_run)
    
    print(f"\n🏃 开始运行 {len(steps_to_run)} 步真实风格转换...")
    start = time.time()
    
    # 进度回调
    def progress_cb(val, msg):
        print(f"\r   [{val*100:.0f}%] {msg}", end="", flush=True)
        if val >= 1.0: print()
        
    results = pipeline.run(context, progress_cb=progress_cb)
    elapsed = time.time() - start
    
    # 7. 保存最终结果
    final_img = context.input_image
    final_path = output_dir / f"real_styles_chain_{int(time.time())}.png"
    final_img.save(final_path)
    
    print("\n" + "=" * 60)
    print(f"🎉 真实风格链式转换完成！总耗时: {elapsed:.2f}s")
    print(f"📁 最终图片已保存: {final_path.resolve()}")
    
    import os
    os.startfile(final_path.resolve())

if __name__ == "__main__":
    main()