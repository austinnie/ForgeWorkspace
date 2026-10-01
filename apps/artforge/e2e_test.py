# apps/artforge/e2e_test.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge 端到端 (E2E) 真实生图测试"""
import sys
import time
from pathlib import Path

# 🔥 1. 注入 ForgeCore 路径
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("=" * 60)
print("🎨 ArtForge E2E 真实生图测试")
print("=" * 60)

try:
    # 🔥 2. 导入 ForgeCore 核心能力
    from forgecore.engines import create_engine
    from forgecore.prompt.composer import PromptComposer
    
    # 3. 准备输出目录
    OUTPUT_DIR = Path(__file__).parent / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 4. 模拟业务逻辑：构建提示词
    print("\n📝 [步骤 1] 构建提示词...")
    
    # 🔥 修复点：字典的值必须是 列表 (List[str])，以符合 PromptComposer 的签名
    preset_layers = {
        "subject": ["1girl, tengu, long nose, red face, feathered wings"],
        "scene": ["deep mountain forest, misty peaks, cherry blossoms"],
        "style": ["ukiyo-e woodblock print, traditional japanese art"],
        "lighting": ["soft moonlight, cinematic lighting"],
        "view": ["full body shot, dynamic angle"],
        "quality": ["masterpiece, best quality, highly detailed, 8k"]
    }
    
    # 传入 layers 字典进行初始化
    composer = PromptComposer(layers=preset_layers)
    
    # 调用 compose_random 随机组合（因为每层只有一个元素，所以结果固定）
    prompt = composer.compose_random(max_tokens=75)
    print(f"   最终 Prompt: {prompt}")
    
    # 5. 调用免费引擎真实生图
    print("\n🚀 [步骤 2] 调用 Pollinations 引擎生成图片...")
    print("   (免费引擎，预计需要 10-30 秒，请耐心等待...)")
    
    engine = create_engine("pollinations")
    
    # 调用 generate_single (根据迁移过来的 PollinationsEngine 签名)
    start_time = time.time()
    image = engine.generate_single(
        prompt=prompt,
        negative="ugly, blurry, low resolution, text, watermark",
        width=768,
        height=768,
        steps=20,
        cfg=7.5
    )
    elapsed = time.time() - start_time
    
    # 6. 保存图片
    print("\n💾 [步骤 3] 保存图片...")
    save_path = OUTPUT_DIR / f"tengu_e2e_test_{int(time.time())}.png"
    image.save(save_path)
    
    print("\n" + "=" * 60)
    print(f"✅ E2E 测试大成功！")
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📁 保存路径: {save_path.resolve()}")
    print("=" * 60)
    
    # 尝试自动打开图片 (Windows)
    import os
    os.startfile(save_path.resolve())

except ImportError as e:
    print(f"\n❌ 导入失败: {e}")
    print("💡 提示: 请检查 forgecore 目录结构是否完整。")
except Exception as e:
    print(f"\n❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()