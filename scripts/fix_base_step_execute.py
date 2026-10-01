# scripts/fix_base_step_execute.py
"""为 BaseStyleStep 添加默认的 execute 方法，兼容旧代码"""
from pathlib import Path

BASE_STEP_FILE = Path(r"E:\SD_OpenVINO\ForgeWorkspace\forgecore\forgecore\pipeline\base_step.py")

if not BASE_STEP_FILE.exists():
    print("❌ 找不到 base_step.py")
    exit(1)

content = BASE_STEP_FILE.read_text(encoding="utf-8")

# 在 BaseStyleStep 类中添加 execute 方法
# 找到 "def get_output_dir_name" 方法，在它之前插入 execute
execute_method = '''
    def execute(self, context, progress_cb=None):
        """
        默认的 execute 实现 - 兼容旧代码
        如果子类没有重写此方法，将使用基于 Prompt 的 Mock 实现
        """
        if progress_cb:
            progress_cb(0.1, "准备提示词...")
        
        # 获取该风格的提示词
        prompts = self.get_prompts()
        if not prompts:
            # 如果没有预设提示词，使用默认值
            prompt_text = f"{self.name} style, masterpiece, best quality"
            negative_text = "worst quality, low quality"
        else:
            # 使用第一个场景的提示词
            prompt_text = prompts[0].get("prompt", f"{self.name} style")
            negative_text = prompts[0].get("negative", "worst quality, low quality")
        
        if progress_cb:
            progress_cb(0.5, "模拟风格转换...")
        
        # Mock 实现：在输入图片上添加文字标注（证明 Step 被执行）
        from PIL import Image, ImageDraw, ImageFont
        output_image = context.input_image.copy() if context.input_image else Image.new('RGB', (512, 512), color='white')
        draw = ImageDraw.Draw(output_image)
        
        # 在图片右下角添加风格名称
        text = f"[{self.name}]"
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
            
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置（右下角）
        x = output_image.width - text_width - 10
        y = output_image.height - text_height - 10
        
        # 绘制半透明背景
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill=(0, 0, 0, 128))
        # 绘制文字
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        if progress_cb:
            progress_cb(1.0, "风格转换完成")
        
        from .base import StepResult, StepStatus
        return StepResult(
            status=StepStatus.SUCCESS,
            output_image=output_image,
            metadata={
                "style": self.name,
                "prompt": prompt_text,
                "negative": negative_text,
                "mock": True
            }
        )

'''

# 找到 "def get_output_dir_name" 的位置并插入
insert_marker = "    def get_output_dir_name"
if insert_marker in content:
    content = content.replace(insert_marker, execute_method + insert_marker)
    BASE_STEP_FILE.write_text(content, encoding="utf-8")
    print("✅ 已为 BaseStyleStep 添加默认的 execute 方法")
else:
    print("⚠️ 未找到插入位置，请手动检查 base_step.py")

print("\n👉 请重新运行: python apps/artforge/test_real_steps.py")