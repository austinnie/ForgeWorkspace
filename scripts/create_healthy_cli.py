# scripts/create_healthy_cli.py
"""生成一个健康的、支持直接输入 Prompt 的 CLI 脚本"""
from pathlib import Path

CLI_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\apps\sd_generator\direct_cli.py")

content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SD Generator 健康版 CLI - 直接输入 Prompt 生图"""
import sys
import os
import torch
from pathlib import Path
from diffusers import StableDiffusionPipeline

# 1. 路径配置 (直接指向真实的模型目录)
REAL_MODELS = Path(r"E:\\SD_OpenVINO\\models")
SD15_DIR = REAL_MODELS / "sd-v1-5"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print(" SD Generator 健康版 CLI 启动")
print("=" * 60)

# 2. 扫描并加载模型
print(f"\\n 扫描模型目录: {SD15_DIR}")
models = list(SD15_DIR.glob("*.safetensors")) + list(SD15_DIR.glob("*.ckpt"))

if not models:
    print("❌ 未找到任何 SD1.5 模型！")
    sys.exit(1)

# 默认使用第一个模型
model_path = models[0]
print(f"📦 准备加载模型: {model_path.name} ({model_path.stat().st_size / 1024**2:.1f} MB)")

print("\\n 正在加载 Diffusers 管道 (首次加载可能需要 20-30 秒)...")
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        str(model_path.parent), # 使用模型所在的目录
        torch_dtype=torch.float32, # CPU 模式下使用 float32
        safety_checker=None, # 关闭安全审查
        requires_safety_checker=False
    )
    # 尝试启用优化 (如果支持)
    if hasattr(pipe, "enable_attention_slicing"):
        pipe.enable_attention_slicing()
    print("✅ 模型加载成功！")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    print("💡 尝试使用 from_single_file 加载...")
    try:
        pipe = StableDiffusionPipeline.from_single_file(
            str(model_path),
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        print("✅ 模型加载成功 (from_single_file)！")
    except Exception as e2:
        print(f"❌ 彻底失败: {e2}")
        sys.exit(1)

# 3. 健康的交互循环
print("\\n" + "=" * 60)
print("💡 使用说明:")
print("   - 直接输入英文 Prompt 进行生图")
print("   - 使用 'prompt | negative prompt' 格式指定反向提示词")
print("   - 输入 'q' 退出")
print("=" * 60)

while True:
    try:
        user_input = input("\\n🎨 请输入 Prompt: ").strip()
        
        if not user_input:
            print("⚠️ 输入为空，请重新输入。")
            continue
            
        if user_input.lower() == 'q':
            print("👋 再见！")
            break
            
        # 解析 Prompt 和 Negative Prompt
        if '|' in user_input:
            prompt, negative_prompt = user_input.split('|', 1)
            prompt = prompt.strip()
            negative_prompt = negative_prompt.strip()
        else:
            prompt = user_input
            negative_prompt = "worst quality, low quality, blurry, bad anatomy"
            
        print(f"\\n🚀 正在生成: '{prompt}'")
        print(f"   反向提示词: '{negative_prompt}'")
        
        # 执行生图
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=20, # 步数
            guidance_scale=7.5,
            width=512,
            height=512
        ).images[0]
        
        # 保存图片
        import time
        timestamp = int(time.time())
        safe_prompt = prompt[:20].replace(" ", "_").replace("/", "_")
        output_path = OUTPUT_DIR / f"cli_{safe_prompt}_{timestamp}.png"
        image.save(output_path)
        
        print(f"✅ 生成成功！已保存至: {output_path}")
        # 自动打开图片 (Windows)
        os.startfile(output_path)
        
    except KeyboardInterrupt:
        print("\\n\\n👋 强制退出！")
        break
    except Exception as e:
        print(f" 生成失败: {e}")
        import traceback
        traceback.print_exc()
'''

CLI_FILE.write_text(content, encoding="utf-8")
print(f"✅ 已生成健康的 CLI 脚本: {CLI_FILE}")
print("\n 请运行: python apps/sd_generator/direct_cli.py")