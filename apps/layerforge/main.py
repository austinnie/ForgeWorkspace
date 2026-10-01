# apps/layerforge/main.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LayerForge - 6层结构化生图 (Monorepo 真实生图版)"""
import sys
import time
from pathlib import Path

# 🔥 1. 注入 ForgeCore 路径
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("🏗️ LayerForge 启动，正在加载 ForgeCore...")

try:
    from forgecore.engines import create_engine
    from forgecore.prompt.composer import PromptComposer

    # 2. 模拟 LayerForge 经典的 6 层配置
    layers_config = {
        "subject": ["1girl, silver hair, blue eyes, futuristic armor"],
        "scene": ["cyberpunk city, neon lights, raining night"],
        "style": ["anime style, cel shading, vivid colors"],
        "lighting": ["cinematic lighting, glowing neon reflections"],
        "view": ["upper body, dynamic pose, looking at viewer"],
        "quality": ["masterpiece, best quality, 8k resolution, highly detailed"]
    }

    # 3. 调用通用提示词构建器
    composer = PromptComposer(layers=layers_config)
    final_prompt = composer.compose_random(max_tokens=75)
    
    print("\n✅ 提示词构建成功！")
    print(f"📝 最终 Prompt:\n{final_prompt}\n")
    
    # 4. 准备输出目录
    OUTPUT_DIR = Path(__file__).parent / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 🔥 5. 真正调用引擎生图！
    engine = create_engine("pollinations")
    print(f"🚀 正在调用 {type(engine).__name__} 生成图片 (预计 10-30 秒)...")
    
    start_time = time.time()
    image = engine.generate_single(
        prompt=final_prompt,
        negative="ugly, blurry, low resolution, text, watermark",
        width=768,
        height=768,
        steps=20,
        cfg=7.5
    )
    elapsed = time.time() - start_time
    
    # 6. 保存图片
    save_path = OUTPUT_DIR / f"layerforge_cyberpunk_{int(time.time())}.png"
    image.save(save_path)
    
    print("\n" + "=" * 50)
    print(f"🎉 LayerForge 真实生图成功！")
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📁 保存路径: {save_path.resolve()}")
    print("=" * 50)
    
    # 尝试自动打开图片 (Windows)
    import os
    os.startfile(save_path.resolve())

except Exception as e:
    print(f"❌ 运行失败: {e}")
    import traceback
    traceback.print_exc()