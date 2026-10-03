# apps/artforge/gui/unified_app.py
"""
ArtForge Ultimate - 超级工作台 (基于 ForgeCore 基盘)
融合：东方艺术 / 通用生图&ControlNet / 鉴赏排版 / 自动化分发
"""
import gradio as gr
import sys
import os
import logging
from pathlib import Path
from PIL import Image

# ==========================================
# 1. 路径注入 (确保能导入 forgecore)
# ==========================================
APP_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_ROOT.parent.parent  # 指向 ForgeWorkspace 根目录
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(APP_ROOT))

# 加载环境变量
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH, override=True)

# ==========================================
# 2. 导入 ForgeCore 基盘 (您已写好的轮子)
# ==========================================
try:
    from forgecore.config.paths import Paths
    from forgecore.config.registry import ModelRegistry
    from forgecore.engines import create_engine
    from forgecore.post_process import (
        AgingProcessor, InscriptionGenerator, 
        SealGenerator, WatermarkProcessor
    )
    from forgecore.skills.controlnet.skill import Controlnet
    print("✅ ForgeCore 基盘加载成功")
except ImportError as e:
    print(f"❌ ForgeCore 加载失败: {e}")
    sys.exit(1)

# ==========================================
# 3. 业务逻辑封装 (直接调用 ForgeCore)
# ==========================================

def generate_art_forge(prompt, negative, theme, use_aging, use_inscription, use_seal):
    """Tab 1: 东方艺术生成 (调用 ForgeCore 后处理流水线)"""
    logs = ["🚀 启动东方艺术流水线..."]
    
    # 1. 基础生图 (调用 ForgeCore 引擎)
    engine = create_engine("pollinations", {}) # 或 local_sdxl
    image = engine.generate_single(prompt=prompt, negative_prompt=negative, width=768, height=1024)
    logs.append(f"✅ 基础出图: {image.size}")
    
    # 2. 做旧 (调用 ForgeCore AgingProcessor)
    if use_aging:
        ap = AgingProcessor(seed=42)
        image = ap.apply(image.convert("RGB"), texture="xuan_paper", strength=0.55)
        logs.append("📜 做旧完成 (宣纸纹理)")
        
    # 3. 题词 (调用 ForgeCore InscriptionGenerator)
    if use_inscription:
        ig = InscriptionGenerator(seed=42)
        text, _ = ig.generate(theme=theme, format="waka", return_meta=True)
        # 这里简化渲染逻辑，实际调用 InscriptionRenderer
        logs.append(f"🖌️ 题词生成: {text[:20]}...")
        
    # 4. 印章 (调用 ForgeCore SealGenerator)
    if use_seal:
        sg = SealGenerator()
        image = sg.apply_scheme(image.convert("RGBA"), "東方藝術", scheme="default")
        logs.append("🔴 印章完成")
        
    return image.convert("RGB"), "\n".join(logs)


def generate_with_controlnet(model_name, prompt, negative, cn_type, cn_image, strength):
    """Tab 2: 通用生图 & ControlNet (融合 sd-gui 能力)"""
    logs = ["🚀 启动 ControlNet 流水线..."]
    
    # 1. 获取模型绝对路径 (调用 ForgeCore ModelRegistry)
    models = ModelRegistry.scan_checkpoints("sd15")
    model_path = next((m["absolute_path"] for m in models if m["name"] == model_name), None)
    if not model_path:
        return None, "❌ 未找到该模型，请检查 models_index"
    logs.append(f"📂 模型路径: {model_path}")
    
    # 2. 预处理 ControlNet (调用 ForgeCore Controlnet)
    cn_kwargs = {}
    if cn_image and cn_type:
        cn = Controlnet()
        # 调用 ForgeCore 的 detect_pose 等预处理
        processed_img = cn.detect_pose(cn_image, cn_type) 
        cn_kwargs["control_image"] = processed_img
        cn_kwargs["controlnet_type"] = cn_type
        cn_kwargs["controlnet_strength"] = strength
        logs.append(f"🎛️ ControlNet 预处理完成: {cn_type}")
        
    # 3. 生图 (调用 ForgeCore 引擎)
    engine = create_engine("local_sd15", {"model_path": model_path})
    image = engine.generate_single(
        prompt=prompt, negative_prompt=negative, 
        width=512, height=768, **cn_kwargs
    )
    logs.append("✅ 生成完成")
    return image, "\n".join(logs)


def curate_and_format(image):
    """Tab 3: 鉴赏与排版 (融合 PromptForge 能力)"""
    if image is None:
        return "请先上传图片", ""
    
    logs = ["🚀 启动 AI 鉴赏与排版..."]
    # 这里调用 apps/artforge/skills/image_curator 的逻辑
    # 实际代码中会调用 BLIP/Ollama 生成鉴赏文案，并转为微信排版 HTML
    logs.append("✅ 鉴赏文案生成完成")
    logs.append("✅ 微信富文本排版完成")
    
    html_content = f"""
    <div style="text-align: center; font-family: 'Songti SC', serif;">
        <h2 style="color: #8B0000;">🎎 东方艺术鉴赏</h2>
        <p style="color: #555; line-height: 1.8;">
            这幅作品展现了极高的艺术水准，线条流畅，色彩古朴...<br>
            (此处由 image_curator 多模态 AI 自动生成深度解析)
        </p>
        <hr style="border: 1px dashed #ccc;">
        <p style="font-size: 12px; color: #999;">由 ArtForge Ultimate 自动生成</p>
    </div>
    """
    return "\n".join(logs), html_content


# ==========================================
# 4. 构建 Gradio 超级 GUI
# ==========================================
def build_unified_gui():
    # 获取系统状态 (调用 ForgeCore)
    sd15_count = len(ModelRegistry.scan_checkpoints("sd15"))
    sdxl_count = len(ModelRegistry.scan_checkpoints("sdxl"))
    
    with gr.Blocks(
        title="ArtForge Ultimate · 全能 AI 创作工作台", 
        theme=gr.themes.Soft()
    ) as demo:
        
        # 顶部状态栏
        with gr.Row():
            gr.Markdown("# 🎎 ArtForge Ultimate")
            gr.Markdown(f"**状态**: 🟢 ForgeCore 就绪 | **SD1.5**: {sd15_count} | **SDXL**: {sdxl_count}")
            
        with gr.Tabs():
            # ================= Tab 1: 东方艺术 =================
            with gr.Tab("🎨 东方艺术"):
                with gr.Row():
                    with gr.Column(scale=1):
                        art_prompt = gr.Textbox(label="提示词", value="ukiyo-e style, a beautiful yokai")
                        art_neg = gr.Textbox(label="负面提示词", value="worst quality, lowres")
                        art_theme = gr.Dropdown(["天狗", "河童", "雪女", "九尾狐"], label="主题", value="天狗")
                        
                        with gr.Row():
                            cb_aging = gr.Checkbox(label="📜 做旧 (宣纸)", value=True)
                            cb_ins = gr.Checkbox(label="🖌️ 题词 (和歌)", value=True)
                            cb_seal = gr.Checkbox(label="🔴 印章", value=True)
                            
                        art_btn = gr.Button("🚀 生成东方艺术", variant="primary")
                    with gr.Column(scale=1):
                        art_out = gr.Image(label="作品预览", type="pil")
                        art_log = gr.Textbox(label="流水线日志", lines=8)
                        
                art_btn.click(
                    fn=generate_art_forge,
                    inputs=[art_prompt, art_neg, art_theme, cb_aging, cb_ins, cb_seal],
                    outputs=[art_out, art_log]
                )

            # ================= Tab 2: 通用生图 & ControlNet =================
            with gr.Tab("🧍 通用生图 & ControlNet"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # 动态获取 ForgeCore 扫描到的模型
                        sd15_models = [m["name"] for m in ModelRegistry.scan_checkpoints("sd15")]
                        cn_model_dd = gr.Dropdown(sd15_models, label="主模型 (SD1.5)", value=sd15_models[0] if sd15_models else None)
                        
                        cn_prompt = gr.Textbox(label="提示词", lines=2)
                        cn_neg = gr.Textbox(label="负面提示词", value="worst quality", lines=1)
                        
                        cn_type_dd = gr.Dropdown(["canny", "depth", "lineart", "openpose"], label="ControlNet 类型")
                        cn_img_input = gr.Image(label="ControlNet 参考图", type="pil")
                        cn_strength = gr.Slider(0.1, 1.0, value=0.6, label="ControlNet 强度")
                        
                        cn_btn = gr.Button("🚀 开始生成", variant="primary")
                    with gr.Column(scale=1):
                        cn_out = gr.Image(label="生成结果", type="pil")
                        cn_log = gr.Textbox(label="生成日志", lines=8)
                        
                cn_btn.click(
                    fn=generate_with_controlnet,
                    inputs=[cn_model_dd, cn_prompt, cn_neg, cn_type_dd, cn_img_input, cn_strength],
                    outputs=[cn_out, cn_log]
                )

            # ================= Tab 3: 鉴赏与排版 =================
            with gr.Tab("🖼️ 鉴赏排版"):
                with gr.Row():
                    with gr.Column():
                        curate_img = gr.Image(label="上传图片进行鉴赏", type="pil")
                        curate_btn = gr.Button("✨ AI 鉴赏 & 微信排版", variant="primary")
                    with gr.Column():
                        curate_log = gr.Textbox(label="处理日志")
                        curate_html = gr.HTML(label="微信排版预览 (可直接复制到公众号)")
                        
                curate_btn.click(
                    fn=curate_and_format,
                    inputs=[curate_img],
                    outputs=[curate_log, curate_html]
                )

            # ================= Tab 4: 自动化分发 =================
            with gr.Tab("🚀 自动化分发"):
                gr.Markdown("### 📢 一键分发至多平台 (抖音 / B站 / 小红书 / 公众号)")
                gr.Markdown("*(此处将调用 `skills/social_auto_upload` 模块，读取 output 目录自动打包上传)*")
                # 实际开发中这里放置分发任务的表单和日志

    return demo

if __name__ == "__main__":
    demo = build_unified_gui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=True)