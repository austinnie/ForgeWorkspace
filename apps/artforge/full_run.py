# apps/artforge/full_run.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ArtForge 终极完整版：提示词构建 -> API生图 -> 保存 -> 自动打开"""
import sys
import time
import os
from pathlib import Path

# 🔥 1. 注入 ForgeCore 路径
CORE_PATH = Path(__file__).resolve().parent.parent.parent / "forgecore"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

print("=" * 60)
print("🎨 ArtForge 终极完整链路测试 (天狗浮世绘)")
print("=" * 60)

try:
    # 🔥 2. 导入 ForgeCore 核心能力
    from forgecore.engines import create_engine
    from forgecore.prompt.composer import PromptComposer
    
    # 3. 准备输出目录
    OUTPUT_DIR = Path(__file__).parent / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 4. 模拟 ArtForge 经典的 6 层预设 (天狗主题)
    print("\n📝 [步骤 1] 构建 6 层结构化提示词...")
    preset_layers = {
        "subject": ["1girl, tengu, long nose, red face, feathered wings, traditional japanese mask"],
        "scene": ["deep mountain forest, misty peaks, falling cherry blossoms, ancient shrine"],
        "style": ["ukiyo-e woodblock print, traditional japanese art, by Hokusai"],
        "lighting": ["soft moonlight, cinematic lighting, glowing aura"],
        "view": ["full body shot, dynamic angle, looking at viewer"],
        "quality": ["masterpiece, best quality, highly detailed, 8k resolution, intricate details"]
    }
    
    composer = PromptComposer(layers=preset_layers)
    final_prompt = composer.compose_random(max_tokens=75)
    print(f"✅ 提示词构建成功:\n   {final_prompt}\n")
    
    # 5. 调用免费引擎真实生图
    print("🚀 [步骤 2] 调用 Pollinations 引擎生成图片...")
    print("   (免费引擎，预计需要 10-30 秒，请耐心等待...)")
    
    engine = create_engine("pollinations")
    
    start_time = time.time()
    
    # 🔥 兼容性处理：旧版引擎可能叫 generate 或 generate_single
    if hasattr(engine, 'generate_single'):
        image = engine.generate_single(
            prompt=final_prompt,
            negative="ugly, blurry, low resolution, text, watermark, modern, 3d",
            width=768,
            height=768,
            steps=25,
            cfg=7.5
        )
    else:
        # 兜底调用通用的 generate 方法
        image = engine.generate(
            prompt=final_prompt,
            negative_prompt="ugly, blurry, low resolution, text, watermark",
            width=768,
            height=768
        )
        
    elapsed = time.time() - start_time
    
    # 6. 保存图片
    print("\n💾 [步骤 3] 保存图片并注入元数据...")
    timestamp = int(time.time())
    save_path = OUTPUT_DIR / f"tengu_ukiyo_e_{timestamp}.png"
    
    # 保存为 PNG
    image.save(save_path)
    
    # (可选) 尝试调用我们搬过来的 EXIF 注入器，让图片看起来像真实相机拍的
    try:
        from forgecore.image.exif_injector import inject_exif
        # 模拟一台富士相机
        inject_exif(save_path, camera="FUJIFILM X-T4", lens="XF 35mm F1.4 R")
        print("   ✅ EXIF 相机元数据注入成功")
    except Exception as e:
        print(f"   ⚠️ EXIF 注入跳过 (不影响出图): {e}")
    
    # 7. 完美收官
    print("\n" + "=" * 60)
    print(f"🎉 终极链路测试大成功！")
    print(f"⏱️  总耗时: {elapsed:.2f} 秒")
    print(f"📁 保存路径: {save_path.resolve()}")
    print(f"📏 图片尺寸: {image.size[0]} x {image.size[1]}")
    print("=" * 60)
    
    # 尝试自动打开图片 (Windows)
    print("\n🖼️  正在为您自动打开图片...")
    os.startfile(save_path.resolve())

except ImportError as e:
    print(f"\n❌ 导入失败: {e}")
    print("💡 提示: 请检查 forgecore 目录结构是否完整。")
except Exception as e:
    print(f"\n❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()